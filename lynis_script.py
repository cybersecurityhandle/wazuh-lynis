import subprocess
import json
import sys
import shutil
import re
import os

# Function to remove ANSI color codes
def remove_ansi_codes(text):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

# Function to run Lynis and capture the output
def run_lynis(lynis_command):
    try:
        # Run Lynis with the specified command and arguments
        result = subprocess.run(lynis_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocess
        print(f"An error occurred while running Lynis: {e}", file=sys.stderr)
        sys.exit(1)

# Function to parse Lynis output into JSON
def parse_lynis_output(output):
    # Remove ANSI color codes
    output_clean = remove_ansi_codes(output)

    # Initialize an empty dictionary to store the parsed data
    parsed_data = {}

    # Regex patterns to identify sections and key-value pairs
    section_pattern = r"\[\+\] (.*?)(?=\n\[)"
    key_value_pattern = r"([^\n:]+):([^\n]+)"

    # Find all sections
    sections = re.findall(section_pattern, output_clean, re.DOTALL)

    for section in sections:
        # Extract the section title
        section_title = section.split("\n")[0].strip()

        # Find all key-value pairs in the section
        key_values = re.findall(key_value_pattern, section)

        # Create a dictionary for each section
        section_data = {key.strip(): value.strip() for key, value in key_values}
        parsed_data[section_title] = section_data

    return parsed_data

# Main function
def main():
    # Define the Lynis command
    lynis_command = ["sudo", "lynis", "audit", "system"]

    # Check if Lynis is installed
    if not shutil.which("lynis"):
        print("Lynis is not installed. Please install Lynis first.", file=sys.stderr)
        sys.exit(1)

    # Run Lynis
    output = run_lynis(lynis_command)

    # Parse the Lynis output
    parsed_output = parse_lynis_output(output)

    # Convert parsed data to JSON
    json_output = json.dumps(parsed_output, indent=4)

    # Output directory
    output_dir = "/var/ossec/logs"

    # Check if output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save to file
    output_file_path = os.path.join(output_dir, 'lynis_output.json')
    with open(output_file_path, 'w') as file:
        file.write(json_output)

    print(f"Lynis output has been saved to {output_file_path}")

# Run the main function
if __name__ == "__main__":
    main()
