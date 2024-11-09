# Replication Package 

This is a replication package for the paper **Checking in with the Action: Revisiting GitHub Action Usage in the Wild**. The package contains files to allow investigation of data collection instruments and data analysis. 

This package include the following structure:

```
. 
+-- data/          # input and output data for the analysis and mining
|   +-- analysis_data/enriched_analysis.csv #the base of most of our analysis
|   +-- output/ # files that are the output of the analysis scripts
|   +-- projects/ # downloaded .github-folder if such existed for project
|   +-- deleted.json # the removed repositories from the search results
|   +-- repositories.json # the final dataset
|
+-- figs/                 # figs that are the output of the analysis scripts
| 
+-- src/          # Files used to collect data from practitioners
|   +-- R/ #R code for statistical testing
|   +-- Java_script/ #javascript for e.g. repository mining
|   +-- Python/ #Python code for some descriptive statistics 
|
+
```
