
import os
from dotenv import load_dotenv
from google.cloud import speech

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# --- GCS Configuration ---
# IMPORTANT: Create a GCS bucket and put its name here.
# https://cloud.google.com/storage/docs/creating-buckets
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


# --- Recognition Configuration ---
# This dictionary is used to configure the Speech-to-Text API.
# See all available options here:
# https://cloud.google.com/speech-to-text/docs/reference/rest/v1/RecognitionConfig

RECOGNITION_CONFIG = {
    # --- Basic Audio Properties ---
    # These should match the audio file you are sending.
    "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
    "sample_rate_hertz": 16000,
    "language_code": "es-419",

    # --- Transcription Improvement Features ---

    # Model selection: 'latest_long' is optimized for long-form audio.
    # Other options: 'telephony', 'medical_conversation', etc.
    #"model": "latest_long",

    # Automatic Punctuation: Adds periods, commas, and question marks.
    #"enable_automatic_punctuation": True,

    # Speaker Diarization: Identifies different speakers in the audio.
    # Uncomment the following lines if your audio has multiple speakers.
    #"enable_speaker_diarization": True,
    #"diarization_config": {
    #    "min_speaker_count": 5,
    #    "max_speaker_count": 10 # Adjust as needed
    #},

    # Phrase Hints (Speech Adaptation): Boosts accuracy for specific words/phrases.
    # This is highly recommended if you have jargon, names, or uncommon words.
    # "speech_contexts": [{
    #     "phrases": ["Gemini CLI", "Luis", "Herramientas"],
    #     "boost": 20.0 # Boost strength from 0 to 20
    # }],
}
