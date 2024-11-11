import os
import re
import json

# Define the path to your data files
data_path = "./data_exfiltration"  # Update this to the actual path

def clean_log_entry(entry):
    """
    Clean and filter each log entry according to specified rules.
    """
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
        return None
    if to_name in ['NULL', 'pipe', '<NA>'] or any(ext in to_name for ext in ['.lib', '.so']):
        return None  # Skip this entry as it's irrelevant

    # Format the observation in a readable "triple" format
    return f"{from_name} → {evt_type} → {to_name}"

def process_text_file(input_file, output_file):
    """
    Process a plain text file where each line is a JSON-like entry.
    """
    cleaned_logs = []

    print(f"Opening file: {input_file}")
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()  # Remove whitespace and newlines
            if not line:
                continue  # Skip empty lines
            
            try:
                # Attempt to parse the line as JSON
                entry = json.loads(line)
                cleaned_entry = clean_log_entry(entry)
                if cleaned_entry:
                    cleaned_logs.append(cleaned_entry)
            except json.JSONDecodeError as e:
                print(f"Skipping line due to JSON decode error: {e}")
                continue  # Skip lines that aren't valid JSON
            
    # Write cleaned entries to the output file
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for log in cleaned_logs:
            out_f.write(log + "\n")
    
    print(f"Processed {len(cleaned_logs)} entries in {input_file}")
    print(f"Cleaned logs saved to {output_file}")

def process_all_text_files(data_path):
    """
    Process all text files in the specified directory.
    """
    for root, _, files in os.walk(data_path):
        for file_name in files:
            if file_name.endswith(".txt"):  # Only process text files
                file_path = os.path.join(root, file_name)
                print(f"Processing file: {file_name}")

                # Define the output file path
                output_file = f"{file_path}_cleaned.txt"
                
                # Process each text file
                process_text_file(file_path, output_file)

# Run the processing for all text files in the data directory
process_all_text_files(data_path)
