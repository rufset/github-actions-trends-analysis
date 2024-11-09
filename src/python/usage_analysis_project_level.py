import pandas as pd
import os

#function that presents by main language the top 10 heaviest when it comes to action usage.  
def calculate_github_actions_usage(csv_folder, csv_filename):
    # Construct the absolute path to the CSV file
    csv_file = os.path.abspath(os.path.join(csv_folder, csv_filename))
    
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Check required columns
    if 'mainLanguage' not in df.columns or 'workflow_ga' not in df.columns:
        print("The CSV file does not contain required columns 'mainLanguage' or 'workflow_ga'.")
        return
    
    # Group by 'mainLanguage' and calculate the counts
    # Count projects with GitHub Actions and without GitHub Actions for each language
    language_usage = df.groupby('mainLanguage').apply(lambda group: pd.Series({
        'with_actions': group['workflow_ga'].gt(0).sum(),
        'without_actions': group['workflow_ga'].le(0).sum()
    })).reset_index()

    # Calculate total projects and percentages for each language
    language_usage['total'] = language_usage['with_actions'] + language_usage['without_actions']
    language_usage['percent_with_actions'] = (language_usage['with_actions'] / language_usage['total']) * 100
    language_usage['percent_without_actions'] = (language_usage['without_actions'] / language_usage['total']) * 100

    # Sort by 'percent_with_actions' in descending order to get top 10 languages
    top_languages = language_usage.sort_values(by='percent_with_actions', ascending=False).head(10)

    # Select columns to display
    result = top_languages[['mainLanguage', 'with_actions', 'without_actions', 'percent_with_actions', 'percent_without_actions']]
    result.columns = ['Language', 'Number with Actions', 'Number without Actions', 'Percent with Actions', 'Percent without Actions']

    # Display the result
    print("Top 10 Languages by GitHub Actions Usage:")
    print(result)

    return result


calculate_github_actions_usage('./data/analysis_data', 'enriched_analysis.csv')


#function for calculating steps etc
def calculate_github_actions_statistics(csv_folder, csv_filename):
    # Construct the absolute path to the CSV file
    csv_file = os.path.abspath(os.path.join(csv_folder, csv_filename))
    
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Check required columns
    if 'workflow_ga' not in df.columns or 'workflow_jobs' not in df.columns or 'workflow_steps' not in df.columns:
        print("The CSV file does not contain required columns 'workflow_ga', 'workflow_jobs', or 'workflow_steps'.")
        return

    # Filter projects with GitHub Actions enabled (workflow_ga > 0)
    df_ga = df[(df['workflow_ga'].notnull()) & (df['workflow_ga'] > 0)]

    # Calculate total counts
    total_projects_with_ga = len(df_ga)
    total_workflows = df_ga['workflow_ga'].sum()
    total_jobs = df_ga['workflow_jobs'].sum()
    total_steps = df_ga['workflow_steps'].sum()

    # Calculate averages
    avg_workflows = df_ga['workflow_ga'].mean()
    avg_jobs = df_ga['workflow_jobs'].mean()
    avg_steps = df_ga['workflow_steps'].mean()

    # Display results
    print("GitHub Actions Statistics for Projects with GA:")
    print(f"Total projects with GitHub Actions: {total_projects_with_ga}")
    print(f"Total number of workflows: {total_workflows}")
    print(f"Average number of workflows: {avg_workflows}")
    print(f"Total number of jobs: {total_jobs}")
    print(f"Average number of jobs: {avg_jobs}")
    print(f"Total number of steps: {total_steps}")
    print(f"Average number of steps: {avg_steps}")

    return {
        "Total Projects with GA": total_projects_with_ga,
        "Total Workflows": total_workflows,
        "Average Workflows": avg_workflows,
        "Total Jobs": total_jobs,
        "Average Jobs": avg_jobs,
        "Total Steps": total_steps,
        "Average Steps": avg_steps
    }


calculate_github_actions_statistics('./data/analysis data', 'enriched_analysis.csv')

