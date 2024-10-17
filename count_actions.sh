#!/bin/bash

# Specify the parent directory containing the project folders
parent_directory="/Users/gomesf/Documents/code_projects/research_projects/github-actions-trends-analysis-main/projects"  # Replace with the actual path to your 
#!/bin/bash

# Specify the output CSV file
output_file="workflow_count.csv"

# Write the CSV header to the output file
echo "project_path;project_name;actions_workflows;workflow_workflows;total" > "$output_file"

# Get a list of all subdirectories (projects) in the parent directory
projects=$(find "$parent_directory" -mindepth 1 -maxdepth 1 -type d)

# Loop through each project folder
for project in $projects; do
    # Define the paths to the .github/actions and .github/workflows directories
    actions_dir="$project/.github/actions"
    workflows_dir="$project/.github/workflows"
    
    # Get the project name from the folder path
    project_name=$(basename "$project")

    # Initialize counts to zero
    count_actions=0
    count_workflows=0

    # Check if the .github/actions directory exists and count .yml and .yaml files
    if [ -d "$actions_dir" ]; then
        count_actions=$(find "$actions_dir" -name "*.yml" -o -name "*.yaml" | wc -l)
    fi

    # Check if the .github/workflows directory exists and count .yml and .yaml files
    if [ -d "$workflows_dir" ]; then
        count_workflows=$(find "$workflows_dir" -name "*.yml" -o -name "*.yaml" | wc -l)
    fi

    # Calculate the total count of files in both actions and workflows directories
    total=$((count_actions + count_workflows))

    # If no files were found in either directory, mark as "empty"
    if [ "$count_actions" -eq 0 ]; then
        count_actions=""
    fi

    if [ "$count_workflows" -eq 0 ]; then
        count_workflows=""
    fi

    if [ "$total" -eq 0 ]; then
        total=""
    fi

    # Write the result to the CSV file
    echo "$project;$project_name;$count_actions;$count_workflows;$total" >> "$output_file"
done

echo "CSV file created: $output_file"


# Write a file to extract per project:
# commits
# stars
# forks
# project language
# contributors
# pull requests
# issues
# watchers