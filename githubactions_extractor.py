import os
import yaml
import csv
import json
import pandas as pd

# Set the parent directory containing the project folders
parent_directory = "/Users/e9linda/Source/github-actions-trends-analysis/projects"
#parent_directory = "/Users/gomesf/Documents/code_projects/research_projects/github-actions-trends-analysis-main/projects" # Replace with the actual path to your projects directory
#output_file = "mini.csv"
output_file = "workflow_analysis.csv"
enriched_output_file = "enriched_analysis.csv"
#enriched_output_file = "miniTest.csv"
#json_files = ['mini1.json', 'mini2.json']
json_files = ['repo1.json', 'repo2.json']

#The code now: iterates over folders, creates a CSV and then enriches with data from the json. If data not available in CSV but is in JSON it adds the data.
#The code should instead: add data from the seart query response json to CSV, then enrich this with data from folders IF there is anything there. If there isn't then they're not utilizing any actions. 

# Define the paths within each project for GitHub actions and workflows
actions_subdir = ".github/actions"
workflows_subdir = ".github/workflows"

# Function to count jobs and steps in a YAML file
def count_jobs_and_steps(yml_file):
    print(yml_file)
    if os.path.exists(yml_file):
        with open(yml_file, 'r') as file:
            try:
                data = yaml.safe_load(file)
            except yaml.YAMLError:
                return 0, 0, 0  # If there's an error parsing the YAML, return 0 for jobs and steps
            except UnicodeDecodeError:
                return 0, 0, 1
            
        jobs_count = 0
        steps_count = 0
        none_count = 0

        if data is None:
            print(yml_file)
            print("-------------------")
            none_count = 1

        if data and 'jobs' in data:
            jobs = data['jobs']
            jobs_count = len(jobs)

            # Count steps for each job
            for job_name, job_data in jobs.items():
                
                if 'steps' == job_name:
                    steps_count += len(job_data['steps'])

                elif isinstance(job_data, dict) and 'steps' in job_data.keys():
                    steps_count += len(job_data['steps'])

        return jobs_count, steps_count, none_count
    else : 
        print("File does not exist")

# Function to analyze a specific subfolder (actions or workflows) for YAML files
def analyze_folder(folder_path):
    yml_count = 0
    total_jobs = 0
    total_steps = 0
    total_nones = 0

    if os.path.exists(folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    yml_count += 1
                    yml_file_path = os.path.join(root, file)
                    jobs, steps, nones = count_jobs_and_steps(yml_file_path)                    
                    total_jobs += jobs
                    total_steps += steps
                    total_nones += nones

    return yml_count, total_jobs, total_steps, total_nones
 

# Open the CSV file for writing
with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Write the header
    csvwriter.writerow(['project', 'workflow_ga', 'workflow_jobs', 'workflow_steps', 'workflow_nones', 'actions_ga', 'actions_jobs', 'actions_steps', 'actions_nones'])
    
    # Loop through all project directories
    for project in os.listdir(parent_directory):
        project_path = os.path.join(parent_directory, project)
        if os.path.isdir(project_path):
            # Analyze .github/workflows directory
            workflows_path = os.path.join(project_path, workflows_subdir)
            workflow_ga, workflow_jobs, workflow_steps, workflow_nones = analyze_folder(workflows_path)
            
            # Analyze .github/actions directory
            actions_path = os.path.join(project_path, actions_subdir)
            actions_ga, actions_jobs, actions_steps, actions_nones = analyze_folder(actions_path)
            
            # Write the results to the CSV
            csvwriter.writerow([project, workflow_ga, workflow_jobs, workflow_steps, workflow_nones, actions_ga, actions_jobs, actions_steps, actions_nones])

print(f"CSV file created: {output_file}")

#Function to enrich the project csv with metadata such as number of stars
def enrich_projects_with_metadata(csv_file, json_files, enriched_output_file):
     # Load all the JSON files and combine them into a single list
    combined_json_data = []

    for json_file in json_files:
        with open(json_file, 'r') as jf:
            json_data = json.load(jf)
            combined_json_data.extend(json_data)  # Add the contents of each JSON file to the combined list

    # Load the CSV into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Define the columns we want to extract and add them if they don't exist
    columns_to_add = ['commits', 'branches', 'totalPullRequests', 'contributors', 
                      'totalIssues', 'stargazers', 'forks', 'watchers', 'mainLanguage']
    
    # Add these columns to the DataFrame if they don't exist
    for col in columns_to_add:
        if col not in df.columns:
            df[col] = None  # Initialize the new column

    # Create a set of existing project names in the CSV to track which projects are already present
    csv_projects = set(df[df.columns[0]].tolist())

    # For each project in the combined JSON list, enrich or add new rows to the CSV
    new_rows = []  # List to hold new rows
    for project_data in combined_json_data:
        # Extract the project name from the "name" field in JSON
        json_project_name = project_data.get("name", "").split('/')[-1]  # Extract the project name after the "/"

        # If the project is already in the CSV, enrich it
        if json_project_name in csv_projects:
            index = df[df[df.columns[0]] == json_project_name].index[0]
            df.at[index, 'commits'] = project_data.get('commits')
            df.at[index, 'branches'] = project_data.get('branches')
            df.at[index, 'totalPullRequests'] = project_data.get('totalPullRequests')
            df.at[index, 'contributors'] = project_data.get('contributors')
            df.at[index, 'totalIssues'] = project_data.get('totalIssues')
            df.at[index, 'stargazers'] = project_data.get('stargazers')
            df.at[index, 'forks'] = project_data.get('forks')
            df.at[index, 'watchers'] = project_data.get('watchers')
            df.at[index, 'mainLanguage'] = project_data.get('mainLanguage')

        # If the project is not in the CSV, add a new row - this is the part that makes the code produce the same result for Github data that are missing the empty folders. 
        else:
            # Prepare the new row
            new_row = {
                df.columns[0]: json_project_name,  # First column is the project name
                'commits': project_data.get('commits'),
                'branches': project_data.get('branches'),
                'totalPullRequests': project_data.get('totalPullRequests'),
                'contributors': project_data.get('contributors'),
                'totalIssues': project_data.get('totalIssues'),
                'stargazers': project_data.get('stargazers'),
                'forks': project_data.get('forks'),
                'watchers': project_data.get('watchers'),
                'mainLanguage': project_data.get('mainLanguage')
            }
            new_rows.append(new_row)  # Add new row to the list

    #If there are new rows, concatenate them to the DataFrame
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)  # Convert list of new rows to a DataFrame
        df = pd.concat([df, new_rows_df], ignore_index=True)  # Concatenate the new rows



    #Save the enriched CSV back to a file
    df.to_csv(enriched_output_file, index=False)

#Calling the enriching function.
enrich_projects_with_metadata(output_file, json_files, enriched_output_file)
print(f"CSV file updated: {enriched_output_file}")
