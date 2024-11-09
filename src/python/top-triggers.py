import os
import yaml
from yaml.resolver import Resolver
import re
from collections import Counter
import csv

# Custom YAML loader to treat `on` as a string even if unquoted since the buillt in yaml loader otherwise interpret it as bool.
def custom_loader(stream):
    # Define a custom constructor to treat 'on' as strings rather than booleans
    def construct_yaml_str(self, node):
        return self.construct_scalar(node)

    # Add the custom constructor to treat YAML boolean-like strings as regular strings
    yaml.SafeLoader.add_constructor('tag:yaml.org,2002:str', construct_yaml_str)
    
    # Remove the implicit boolean resolver specifically for 'on'
    # This prevents automatic conversion of that keywords to booleans
    bool_keywords = ['on']
    for keyword in bool_keywords:
        if keyword[0].lower() in Resolver.yaml_implicit_resolvers:
            Resolver.yaml_implicit_resolvers[keyword[0].lower()] = [
                entry for entry in Resolver.yaml_implicit_resolvers[keyword[0].lower()]
                if entry[0] != 'tag:yaml.org,2002:bool'
            ]

    # Parse the YAML with the custom SafeLoader
    return yaml.load(stream, Loader=yaml.SafeLoader)

def extract_on_event_counts(base_folder, on_event_output_csv, error_log, no_on_log):
    # Initialize counter for "on" events
    on_event_counter = Counter()

    # Open the error log and "no on key" log files for writing
    with open(error_log, 'w') as error_file, open(no_on_log, 'w') as no_on_file:
        # Traverse through each subdirectory in the base folder
        for root, dirs, files in os.walk(base_folder):
            # Check if the folder structure corresponds to a workflows folder inside a .github directory
            if os.path.basename(root) == "workflows" and ".github" in root.split(os.sep):
                found_on_key = False  # Flag to check if any file has an "on" key in this directory
                
                for file_name in files:
                    if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                        file_path = os.path.join(root, file_name)
                        
                        try:
                            with open(file_path, 'r') as yaml_file:
                                workflow_data = custom_loader(yaml_file)
                                
                                # Skip if workflow_data is None
                                if workflow_data is None:
                                    continue
                                
                                # Check if "on" key is present in the YAML data
                                if "on" in workflow_data:
                                    found_on_key = True
                                    on_events = workflow_data["on"]

                                    # Process each type of configuration for the "on" key
                                    if isinstance(on_events, dict):
                                        # Each key within `on` should be counted as an individual event
                                        for event in on_events.keys():
                                            on_event_counter[event] += 1
                                            print(f"Added event '{event}' from {file_path}")  # Debug print
                                    elif isinstance(on_events, list):
                                        for event in on_events:
                                            on_event_counter[event] += 1
                                            print(f"Added event '{event}' from {file_path}")  # Debug print
                                    elif isinstance(on_events, str):
                                        on_event_counter[on_events] += 1
                                        print(f"Added event '{on_events}' from {file_path}")  # Debug print

                        except yaml.YAMLError as e:
                            error_file.write(f"YAML error in {file_path}: {e}\n")
                        except Exception as e:
                            error_file.write(f"Unexpected error in {file_path}: {e}\n")

                # Log the top-level folder if no "on" key was found in any YAML file within this workflows directory
                if not found_on_key:
                    top_folder = root.split(os.sep)[1]  # Get the top-level folder name
                    no_on_file.write(f"{top_folder}\n")

    # Write the on_event_counter to the specified CSV file
    with open(on_event_output_csv, 'w', newline='') as on_event_csv_file:
        writer = csv.writer(on_event_csv_file)
        writer.writerow(['Event', 'Count'])  # Write header
        for event, count in on_event_counter.items():
            writer.writerow([event, count])

# Run the function with specified paths
extract_on_event_counts(
    base_folder='./data/projects',
    on_event_output_csv='./data/output/on_event_counts.csv',
    error_log='./data/output/yaml_errors.txt',
    no_on_log='./data/output/no_on_key_projects.txt'
)
