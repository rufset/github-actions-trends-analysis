import os
import yaml
import csv

# Set the parent directory containing the project folders
parent_directory = "/Users/gomesf/Documents/code_projects/research_projects/github-actions-trends-analysis-main/projects" # Replace with the actual path to your projects directory
output_file = "workflow_analysis.csv"

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
