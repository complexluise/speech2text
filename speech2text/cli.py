import click
import json
from pathlib import Path

from speech2text.logger_setup import log
from speech2text.config import RECOGNITION_CONFIG, GCS_BUCKET_NAME
from speech2text import speech_service

# Define the path to the jobs directory
JOBS_DIR = Path(__file__).parent.parent / "jobs"
JOBS_DIR.mkdir(exist_ok=True)

@click.group()
def cli():
    """A CLI tool to transcribe audio files using Google Speech-to-Text."""
    pass

@cli.command()
@click.argument("audio_path", type=click.Path(exists=True))
@click.option('--timeout', default=3600, help='Seconds to wait for the transcription to complete.')
def transcribe(audio_path: str, timeout: int):
    """
    Uploads an audio file, starts transcription, and waits for the result.
    """
    if not GCS_BUCKET_NAME or GCS_BUCKET_NAME == "your-gcs-bucket-name-here":
        log.error("[bold red]GCS_BUCKET_NAME is not configured in speech2text/config.py[/bold red]")
        log.error("Please create a GCS bucket and update the config file.")
        return

    audio_path = Path(audio_path).resolve()
    job_name = audio_path.stem
    job_file = JOBS_DIR / f"{job_name}.json"

    # 1. Upload to GCS
    gcs_uri = speech_service.upload_to_gcs(
        local_file_path=str(audio_path),
        bucket_name=GCS_BUCKET_NAME,
        destination_blob_name=audio_path.name
    )

    if not gcs_uri:
        log.error("[bold red]Could not start job because GCS upload failed.[/bold red]")
        return

    # 2. Start transcription job
    operation = speech_service.start_transcription_job(
        gcs_uri=gcs_uri,
        config=RECOGNITION_CONFIG
    )

    if not operation:
        log.error("[bold red]Failed to start transcription operation.[/bold red]")
        return

    log.info(f"Successfully started job. Operation name: {operation.operation.name}")
    log.info(f"Waiting for job to complete... (Timeout: {timeout} seconds)")

    # 3. Wait for completion and get result
    try:
        # The .result() method blocks until the operation is complete
        # and returns the final result. It handles polling automatically.
        result = operation.result(timeout=timeout)

        log.info("[bold green]Job is DONE.[/bold green]")
        
        transcript = ""
        for res in result.results:
            transcript += res.alternatives[0].transcript + "\n"
        
        # 4. Save the final result to JSON
        job_data = {
            "job_name": job_name,
            "operation_name": operation.operation.name,
            "status": "DONE",
            "audio_file": str(audio_path),
            "gcs_uri": gcs_uri,
            "transcript": transcript.strip()
        }
        
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=4)
            
        log.info("--- Transcript ---")
        log.info(transcript.strip())
        log.info("------------------")
        log.info(f"Full job details saved to: {job_file}")

    except Exception as e:
        log.error(f"[bold red]An error occurred while waiting for the result:[/bold red] {e}")
        job_data = {
            "job_name": job_name,
            "operation_name": operation.name,
            "status": "ERROR",
            "error_message": str(e)
        }
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=4)

if __name__ == "__main__":
    cli()