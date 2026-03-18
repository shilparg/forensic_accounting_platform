import json
import os

input_filepath = 'output/raw_sec_filings.jsonl'
output_filepath = 'bq_ready_filings.jsonl'

valid_records = 0

try:
    print(f"Reading from {input_filepath}...")
    with open(input_filepath, 'r') as infile, open(output_filepath, 'w') as outfile:
        for line in infile:
            try:
                row = json.loads(line.strip())
                # Pull out the actual SEC filing data hidden inside 'document'
                if 'document' in row:
                    clean_record = row['document']
                    outfile.write(json.dumps(clean_record) + '\n')
                    valid_records += 1
            except json.JSONDecodeError:
                continue

    print(f"Success! Extracted {valid_records} clean SEC filings.")
    print(f"Your BigQuery-ready file is: {output_filepath}")

except FileNotFoundError:
    print(f"Error: Could not find {input_filepath}. Make sure you ran the meltano command!")