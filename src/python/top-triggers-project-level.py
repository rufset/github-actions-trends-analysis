import os
import yaml
from yaml.resolver import Resolver
import csv
from collections import Counter

# Custom YAML loader to treat `on` as a string even if unquoted
def custom_loader(stream):
    def construct_yaml_str(self, node):
        return self.construct_scalar(node)

    yaml.SafeLoader.add_constructor('tag:yaml.org,2002:str', construct_yaml_str)

    # Remove implicit boolean resolver for `on`
    bool_keywords = ['on']
    for keyword in bool_keywords:
        if keyword[0].lower() in Resolver.yaml_implicit_resolvers:
            Resolver.yaml_implicit_resolvers[keyword[0].lower()] = [
                entry for entry in Resolver.yaml_implicit_resolvers[keyword[0].lower()]
                if entry[0] != 'tag:yaml.org,2002:bool'
            ]

    return yaml.load(stream, Loader=yaml.SafeLoader)

# Main function
def extract_on_event_counts(base_folder, on_event_output_csv, error_log, no_on_log):
    on_event_counter = Counter()

    with open(error_log, 'w') as error_file, open(no_on_log, 'w') as no_on_file:
        for root, dirs, files in os.walk(base_folder):
            # Identify a `.github/workflows` folder
            if os.path.basename(root) == "workflows" and ".github" in root.split(os.sep):
                found_on_key = False
                project_events = set()  # To store unique events found within this project folder
                
                for file_name in files:
                    if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                        file_path = os.path.join(root, file_name)
                        
                        try:
                            with open(file_path, 'r') as yaml_file:
                                workflow_data = custom_loader(yaml_file)

                                if workflow_data is None:
                                    continue
                                
                                # Check for the `on` key
                                if "on" in workflow_data:
                                    found_on_key = True
                                    on_events = workflow_data["on"]

                                    if isinstance(on_events, dict):
                                        # Process each event under `on`
                                        for event in on_events.keys():
                                            if event not in project_events:
                                                project_events.add(event)
                                                on_event_counter[event] += 1
                                                print(f"Added event '{event}' from {file_path}")  # Debug print
                                    elif isinstance(on_events, list):
                                        for event in on_events:
                                            if event not in project_events:
                                                project_events.add(event)
                                                on_event_counter[event] += 1
                                                print(f"Added event '{event}' from {file_path}")  # Debug print
                                    elif isinstance(on_events, str):
                                        if on_events not in project_events:
                                            project_events.add(on_events)
                                            on_event_counter[on_events] += 1
                                            print(f"Added event '{on_events}' from {file_path}")  # Debug print

                        except yaml.YAMLError as e:
                            error_file.write(f"YAML error in {file_path}: {e}\n")
                        except Exception as e:
                            error_file.write(f"Unexpected error in {file_path}: {e}\n")

                if not found_on_key:
                    top_folder = root.split(os.sep)[1]
                    no_on_file.write(f"{top_folder}\n")

    # Write the on_event_counter to the CSV
    with open(on_event_output_csv, 'w', newline='') as on_event_csv_file:
        writer = csv.writer(on_event_csv_file)
        writer.writerow(['Event', 'Count'])
        for event, count in on_event_counter.items():
            writer.writerow([event, count])

# Run the function
extract_on_event_counts(
    base_folder='projects',
    on_event_output_csv='on_event_counts_project.csv',
    error_log='yaml_errors_project.txt',
    no_on_log='no_on_key_projects_projects.txt'
)
