import click
import json
from pathlib import Path

from google.longrunning.operations_pb2 import Operation, GetOperationRequest
from speech2text.logger_setup import log
from speech2text.config import RECOGNITION_CONFIG, GCS_BUCKET_NAME
from speech2text import speech_service

# Define the path to the jobs directory
JOBS_DIR = Path(__file__).parent.parent / "jobs"
JOBS_DIR.mkdir(exist_ok=True)

@click.group()
def cli():
    """A CLI tool to manage Google Speech-to-Text jobs via GCS."""
    pass

@cli.command()
@click.argument("audio_path", type=click.Path(exists=True))
def start(audio_path: str):
    """Uploads an audio file to GCS and starts a transcription job."""
    if not GCS_BUCKET_NAME or GCS_BUCKET_NAME == "your-gcs-bucket-name-here":
        log.error("[bold red]GCS_BUCKET_NAME is not configured in speech2text/config.py[/bold red]")
        log.error("Please create a GCS bucket and update the config file.")
        return

    audio_path = Path(audio_path).resolve()
    job_name = audio_path.stem
    job_file = JOBS_DIR / f"{job_name}.json"

    if job_file.exists():
        log.warning(f"[bold yellow]Job '{job_name}' already exists. Overwrite?.[/bold yellow]")
        click.confirm("Do you want to continue?", abort=True)

    # 1. Upload to GCS
    gcs_uri = speech_service.upload_to_gcs(
        local_file_path=str(audio_path),
        bucket_name=GCS_BUCKET_NAME,
        destination_blob_name=audio_path.name
    )

    if not gcs_uri:
        log.error("[bold red]Could not start job because GCS upload failed.[/bold red]")
        return

    # 2. Start transcription job with GCS URI
    operation: Operation = speech_service.start_transcription_job(
        gcs_uri=gcs_uri,
        config=RECOGNITION_CONFIG
    )

    if operation:
        job_data = {
            "job_name": job_name,
            "operation_name": operation.operation.name,
            "operation_name_field_number": operation.operation.NAME_FIELD_NUMBER,
            "status": "RUNNING",
            "audio_file": str(audio_path),
            "gcs_uri": gcs_uri
        }
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=4)

        log.info(f"[bold green]Successfully started job '{job_name}'[/bold green]")
        log.info(f"Job details saved to: {job_file}")
        log.info(f"To check status, run: [bold]python -m speech2text.cli check {job_name}[/bold]")

@cli.command()
@click.argument("job_name", type=str)
def check(job_name: str):
    """Checks the status of a transcription job."""
    job_file = JOBS_DIR / f"{job_name}.json"

    if not job_file.exists():
        log.error(f"[bold red]Job '{job_name}' not found. Looked for: {job_file}[/bold red]")
        return

    with open(job_file, "r") as f:
        job_data = json.load(f)

    operation_name = job_data.get("operation_name")
    operation_name_field_number = job_data.get("operation_name_field_number")
    
    operation_request = GetOperationRequest(
        name=operation_name,
        #NAME_FIELD_NUMBER=operation_name_field_number
    )
    if not operation_request.name:
        log.error(f"[bold red]'operation_name' not found in {job_file}[/bold red]")
        return

    operation: Operation = speech_service.check_job_status(operation_request)

    if operation and operation.done:
        log.info(f"[bold green]Job '{job_name}' is DONE.[/bold green]")
        job_data["status"] = "DONE"
        response = operation.result(timeout=90)
        transcript_builder = []
        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
            transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")

        transcript = "".join(transcript_builder)
        
        job_data["transcript"] = transcript.strip()
        
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=4)
            
        log.info("--- Transcript ---")
        log.info(transcript.strip())
        log.info("------------------")
        log.info(f"Updated job file: {job_file}")

    elif operation:
        log.info(f"[bold yellow]Job '{job_name}' is still RUNNING.[/bold yellow]")
    else:
        log.error(f"[bold red]Could not retrieve status for job '{job_name}'.[/bold red]")

@cli.command()
@click.argument("job_name", type=str)
def get(job_name: str):
    """Gets the transcript for a completed job from the local JSON file."""
    job_file = JOBS_DIR / f"{job_name}.json"

    if not job_file.exists():
        log.error(f"[bold red]Job '{job_name}' not found. Looked for: {job_file}[/bold red]")
        return

    with open(job_file, "r") as f:
        job_data = json.load(f)

    if job_data.get("status") == "DONE" and "transcript" in job_data:
        log.info(f"--- Transcript for Job '{job_name}' ---")
        log.info(job_data['transcript'])
        log.info("------------------------------------")
    elif job_data.get("status") == "RUNNING":
        log.warning(f"[bold yellow]Job '{job_name}' is still running.[/bold yellow]")
        log.info(f"Run [bold]python -m speech2text.cli check {job_name}[/bold] to update its status.")
    else:
        log.error(f"[bold red]Transcript not available for job '{job_name}'.[/bold red]")
        log.info(f"Try running the 'check' command first.")

if __name__ == "__main__":
    cli()