import json

def merge_json_files(file1, file2, output_file):
    # Load data from the first JSON file
    with open(file1, 'r') as f1:
        data1 = json.load(f1)
    
    # Load data from the second JSON file
    with open(file2, 'r') as f2:
        data2 = json.load(f2)
    
    # Merge the two lists
    merged_data = data1 + data2

    # Convert each element to a JSON string, deduplicate, and convert back to dictionaries
    unique_data = list({json.dumps(item, sort_keys=True) for item in merged_data})
    unique_data = [json.loads(item) for item in unique_data]
    
    # Save the merged data to the output file
    with open(output_file, 'w') as outfile:
        json.dump(unique_data, outfile, indent=4)

# Example usage
merge_json_files('repo1.json', 'repo2.json', 'merged_output.json')