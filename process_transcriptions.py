

import json
import os
import argparse

def process_transcriptions(job_name):
    job_folder = os.path.join('jobs', job_name)
    if not os.path.isdir(job_folder):
        print(f"Error: Job folder '{job_folder}' not found.")
        return

    transcriptions = []
    for filename in os.listdir(job_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(job_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'transcript' in data:
                    transcriptions.append(data['transcript'])

    if not transcriptions:
        print(f"No transcriptions found in job '{job_name}'.")
        return

    output_filename = f"{job_name}_transcription_raw.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(transcriptions))

    print(f"Successfully processed transcriptions for job '{job_name}'.")
    print(f"Output saved to '{output_filename}'.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process transcriptions from a job.')
    parser.add_argument('job_name', help='The name of the job to process (e.g., mesa_1).')
    args = parser.parse_args()
    process_transcriptions(args.job_name)

