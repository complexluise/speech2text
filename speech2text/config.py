# --- GCS Configuration ---
# IMPORTANT: Create a GCS bucket and put its name here.
# https://cloud.google.com/storage/docs/creating-buckets
GCS_BUCKET_NAME = "bucket-for-everything"


from google.cloud import speech

# --- Recognition Configuration ---
# You can customize this dictionary to match your audio file's properties.
# See all available options here:
# https://cloud.google.com/speech-to-text/docs/reference/rest/v1/RecognitionConfig

RECOGNITION_CONFIG = {
    "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
    "sample_rate_hertz": 16000,
    "language_code": "es-419",
    # Add other options like 'profanity_filter', 'enable_automatic_punctuation', etc.
}