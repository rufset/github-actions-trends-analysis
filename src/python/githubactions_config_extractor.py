import os
import yaml
from collections import Counter
import csv

def map_runs_on_value(runs_on_value):
    """Map runs_on values to predefined categories."""
    if isinstance(runs_on_value, list):
        # Handle the case where runs_on is a list
        return [map_runs_on_value(value) for value in runs_on_value]
    runs_on_value = str(runs_on_value).lower()
    if 'ubuntu' in runs_on_value:
        return 'ubuntu'
    elif 'windows' in runs_on_value:
        return 'Windows'
    elif 'macos' in runs_on_value or 'mac' in runs_on_value:
        return 'MacOs'
    elif 'self-host' in runs_on_value or 'self-hosted' in runs_on_value:
        return 'self-host'
    else:
        return runs_on_value  # Return the original if it doesn't match predefined categories

def extract_actions_and_runs_on_counts(base_folder, uses_output_csv, runs_on_output_csv, error_log):
    # Initialize counters
    uses_counter = Counter()
    runs_on_counter = Counter()
    matrix_counter = Counter()

    # Open the error log file for writing
    with open(error_log, 'w') as error_file:
        # Traverse through each subdirectory in the base folder
        for root, dirs, files in os.walk(base_folder):
            if os.path.basename(root) == "workflows" and ".github" in root.split(os.sep):
                for file_name in files:
                    if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                        file_path = os.path.join(root, file_name)
                        print(f"Processing file: {file_path}")  # Diagnostic output
                        
                        with open(file_path, 'r') as yaml_file:
                            try:
                                workflow_data = yaml.safe_load(yaml_file)
                                if workflow_data is None:
                                    error_file.write(f"Error: {file_path} returned None\n")
                                    continue  

                                if "jobs" in workflow_data:
                                    # Iterate over each job in the jobs section
                                    for job_name, job in workflow_data["jobs"].items():
                                        # Process "steps" to count "uses"
                                        if "steps" in job:
                                            for step in job["steps"]:
                                                if "uses" in step:
                                                    action_name = step["uses"].split('@')[0]  # Get "fu/bar" part
                                                    uses_counter[action_name] += 1

                                        # Check for "strategy" with "matrix"
                                        if "strategy" in job and "matrix" in job["strategy"]:
                                            if "os" in job["strategy"]["matrix"]:
                                                matrix_counter["matrix"] += 1  # Count as one for matrix
                                        else:
                                            # Process "runs-on" value only if strategy.matrix is not present
                                            if "runs-on" in job:
                                                runs_on_value = job["runs-on"]
                                                # Map to predefined categories
                                                if isinstance(runs_on_value, list):
                                                    for value in runs_on_value:
                                                        mapped_value = map_runs_on_value(value)
                                                        runs_on_counter[mapped_value] += 1
                                                else:
                                                    mapped_value = map_runs_on_value(runs_on_value)
                                                    runs_on_counter[mapped_value] += 1

                            except yaml.YAMLError as e:
                                error_file.write(f"Error parsing {file_path}: {e}\n")
                                print(f"YAML parsing error in {file_path}: {e}")  # Optional print for visibility
                            except Exception as e:
                                error_file.write(f"Unexpected error with {file_path}: {e}\n")
                                print(f"Unexpected error in {file_path}: {e}")  # Optional print for visibility

    # Write uses_counter to CSV
    with open(uses_output_csv, 'w', newline='') as uses_csv_file:
        writer = csv.writer(uses_csv_file)
        writer.writerow(['Action', 'Count'])  # Write header
        for action, count in uses_counter.items():
            writer.writerow([action, count])

    # Write runs_on_counter and matrix counts to CSV
    with open(runs_on_output_csv, 'w', newline='') as runs_on_csv_file:
        writer = csv.writer(runs_on_csv_file)
        writer.writerow(['Runs On', 'Count'])  # Write header
        for runs_on_value, count in runs_on_counter.items():
            writer.writerow([runs_on_value, count])
        
        # Add matrix counts under a single 'matrix' label
        if "matrix" in matrix_counter:
            writer.writerow(['matrix', matrix_counter["matrix"]])  # Write combined matrix count

# Call the function as needed
extract_actions_and_runs_on_counts(
    base_folder='projects',
    uses_output_csv='actions_counts.csv',
    runs_on_output_csv='runs_on_counts.csv',
    error_log='yaml_errors.txt'
)