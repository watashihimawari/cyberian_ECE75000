import os
import ijson
import re

# Define the path to your data files
data_path = "./omid"  # Update this to the actual path

def clean_log_entry(entry):
    from_name = entry.get('from_name', '')
    evt_type = entry.get('evt_type', '')
    to_name = entry.get('to_name', '')

    # Apply renaming rules
    if from_name in ['sh', 'zsh', '-bash']:
        from_name = 'bash'
    if re.match(r'^tmp\d+$', to_name):
        to_name = 'temp process'
    if to_name in ['sh', 'zsh', '-bash']:
        to_name = 'bash'

    # Filter out irrelevant events
    if from_name in ['NULL', 'pipe', '<NA>'] or any(ext in from_name for ext in ['.lib', '.so']):
        print(f"Skipping entry: {entry}")
        return None
    if to_name in ['NULL', 'pipe', '<NA>'] or any(ext in to_name for ext in ['.lib', '.so']):
        print(f"Skipping entry: {entry}")
        return None  # Skip this entry as it's irrelevant

    # Format the observation in triple format
    return f"{from_name} → {evt_type} → {to_name}"

def process_file(file_path):
    cleaned_logs = []
    
    print(f"Opening file: {file_path}")
    
    with open(file_path, 'r') as f:
        try:
            # Use ijson to parse JSON objects one by one
            for entry in ijson.items(f, 'item'):
                cleaned_entry = clean_log_entry(entry)
                if cleaned_entry:
                    cleaned_logs.append(cleaned_entry)
                    
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []
    
    print(f"Processed {len(cleaned_logs)} entries in {file_path}")
    return cleaned_logs

def process_all_files(data_path):
    for root, _, files in os.walk(data_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            print(f"Processing file: {file_name}")

            cleaned_logs = process_file(file_path)

            # Save the cleaned logs to a new file with utf-8 encoding
            output_file = f"{file_path}_cleaned.txt"
            with open(output_file, 'w', encoding='utf-8') as out_f:
                for log in cleaned_logs:
                    out_f.write(log + "\n")
            print(f"Cleaned logs saved to {output_file}")

process_all_files(data_path)
