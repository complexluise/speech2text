from google.cloud import speech, storage
from google.longrunning.operations_pb2 import GetOperationRequest, Operation
from speech2text.logger_setup import log

def upload_to_gcs(local_file_path: str, bucket_name: str, destination_blob_name: str):
    """Uploads a file to the GCS bucket and returns its GCS URI."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        log.info(f"[bold blue]Uploading {local_file_path} to gs://{bucket_name}/{destination_blob_name}[/bold blue]")
        blob.upload_from_filename(local_file_path)
        gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
        log.info(f"[bold green]Upload complete. URI: {gcs_uri}[/bold green]")
        return gcs_uri
    except Exception as e:
        log.error(f"[bold red]GCS upload failed:[/bold red] {e}")
        return None

def start_transcription_job(gcs_uri: str, config: dict):
    """Initiates a long-running speech recognition job from a GCS URI."""
    log.info(f"[bold blue]Starting transcription for:[/bold blue] {gcs_uri}")
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    recognition_config = speech.RecognitionConfig(**config)

    try:
        operation: Operation = client.long_running_recognize(
            config=recognition_config, audio=audio
        )
        log.info("[bold green]API call successful. Operation started.[/bold green]")
        return operation
    except Exception as e:
        log.error(f"[bold red]API call failed:[/bold red] {e}")
        return None

