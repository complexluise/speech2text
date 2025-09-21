import click
import json
from pathlib import Path
import glob
from rich.progress import Progress, SpinnerColumn, TextColumn

from speech2text.logger_setup import log
from speech2text.config import RECOGNITION_CONFIG, GCS_BUCKET_NAME
from speech2text import speech_service, llm_service

# Define the path to the jobs directory
JOBS_DIR = Path(__file__).parent.parent / "jobs"
JOBS_DIR.mkdir(exist_ok=True)

@click.group()
def cli():
    """A CLI tool to transcribe and process audio files."""
    pass

@cli.command()
@click.argument("job_directory", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--output", type=click.Path(file_okay=True, dir_okay=False, resolve_path=True), default=None, help="Path for the output Markdown file.")
@click.option("--context-words", default=100, help="Number of words from the end of the document to use as context for the next chunk.")
def post_process(job_directory: str, output: str, context_words: int):
    """
    Combines, corrects, and structures transcription JSON files into a Markdown document using an LLM.
    """
    log.info(f"Starting post-processing for job directory: {job_directory}")
    job_dir = Path(job_directory)

    # --- 1. Find and sort transcription part files ---
    json_files = sorted(glob.glob(f"{job_dir}/*_part_*.json"))
    if not json_files:
        log.error(f"[bold red]No '_part_*.json' files found in {job_dir}.[/bold red]")
        log.error("Please specify a directory containing transcription parts.")
        return

    log.info(f"Found {len(json_files)} transcription parts to process.")

    # --- 2. Phase 1: Individual Correction ---
    corrected_chunks = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Phase 1: Correcting text chunks...", total=len(json_files))
        for i, file_path in enumerate(json_files):
            progress.update(task, description=f"Phase 1: Correcting chunk {i+1}/{len(json_files)}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    transcript = data.get("transcript", "")
                    if transcript:
                        corrected = llm_service.correct_text_chunk(transcript)
                        if corrected:
                            corrected_chunks.append(corrected)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                log.warning(f"Could not read or parse {file_path}: {e}")
        progress.update(task, completed=True, description="Phase 1 Complete.")
    
    if not corrected_chunks:
        log.error("[bold red]No text could be extracted or corrected from the JSON files.[/bold red]")
        return

    log.info("All text chunks corrected successfully.")

    # --- 3. Phase 2: Iterative Structuring and Joining ---
    final_document = ""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Phase 2: Structuring document...", total=len(corrected_chunks))
        
        # Initialize document with the first chunk
        progress.update(task, description="Phase 2: Structuring initial chunk...")
        final_document = llm_service.structure_initial_chunk(corrected_chunks[0])
        progress.update(task, advance=1)

        # Iteratively join the rest of the chunks
        for i, new_chunk in enumerate(corrected_chunks[1:]):
            progress.update(task, description=f"Phase 2: Structuring and joining chunk {i+2}/{len(corrected_chunks)}")
            
            # Get the last ~N words as context
            context = " ".join(final_document.split()[-context_words:])
            
            structured_addition = llm_service.structure_and_join_chunk(
                previous_context=context,
                new_chunk=new_chunk
            )
            
            if structured_addition:
                final_document += "\n\n" + structured_addition
            
            progress.update(task, advance=1)
        progress.update(task, completed=True, description="Phase 2 Complete.")

    log.info("[bold green]Document structuring complete.[/bold green]")

    # --- 4. Save the final document ---
    if output:
        output_path = Path(output)
    else:
        output_path = job_dir.parent / f"{job_dir.name}.md"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_document)
        log.info(f"Final Markdown document saved to: {output_path}")
    except IOError as e:
        log.error(f"[bold red]Failed to write output file to {output_path}:[/bold red] {e}")


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