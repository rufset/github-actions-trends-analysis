library(tidyverse)
library(effsize)


# Custom color palette for the plots
my_palette <- c("#EBD9B2","#D9B466","#aed9d6","#5BB4AC","#9A609A","#5B507A","#74A1CF","#083D77","#888888")

# Function to remove outliers from data for future analysis.
del_outliers_iqr <- function(data_df, column) {
  filtered_df <- data_df %>% 
    group_by(Group) %>% 
    mutate(IQR = IQR(!!sym(column)),
           O_upper = quantile(!!sym(column), probs=c( .75), na.rm = FALSE)+1.5*IQR,  
           O_lower = quantile(!!sym(column), probs=c( .25), na.rm = FALSE)-1.5*IQR) %>% 
    filter(O_lower <= !!sym(column) & !!sym(column) <= O_upper)
  return(filtered_df)
}

# ------------------------------------------------------------
# Step 1: Load the dataset with data from all projects
# ------------------------------------------------------------
raw_data_df <- read.csv("./data/analysis_data/enriched_analysis.csv") %>% 
  mutate(totalIssues = ifelse(is.na(totalIssues), 0, totalIssues))

# RQ1: Analysis of Programming Languages
# Generate the data frame with projects per programming language.
languages_df <- raw_data_df %>% 
  select(mainLanguage, workflow_ga) %>%
  group_by(mainLanguage) %>% 
  summarise(Count = n(), 
            WithoutWorkflows = sum(workflow_ga == 0), 
            WithWorkflow     = sum(workflow_ga > 0)) %>% 
  mutate(PercProjs    = round(100*Count/sum(Count)  ,1),
         PercAdoption = round(100*WithWorkflow/Count,1))

# Create the plot for adoption rate per programming language.
lang_plot <- ggplot(languages_df, aes(x = reorder(mainLanguage, -PercAdoption), y = PercAdoption, label = paste(PercProjs,"%"))) +
  geom_col(width = 0.8, fill = "#5BB4AC") +
  geom_hline(yintercept = 50, linetype = "dashed") +
  geom_text(aes(y = 5), vjust = -0.5, size = 3) +
  scale_y_continuous(breaks = seq(0,100,by=20), limits = c(0,100)) +
  labs(y = "Perc. of GA Adoption", x = "Programming Languages") +
  theme_bw() + theme(text=element_text(size=15), axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1), legend.position = "none")

# Save into a file.
ggsave(lang_plot, filename = "./figs/LanguagePlot.pdf", device = cairo_pdf(), width = 25, height = 12, units = "cm")


# RQ1: Analysis of Stars per Project
# Create a discretised data frame with information of the stars per project.
stars_df <- raw_data_df %>% 
  arrange(stargazers) %>% 
  mutate(StarGroup = factor((floor(row_number()/1000))),
         StarSubgroup = factor((floor(row_number()/200))))

# Summarise the information from all projects to compare projects with and
#.  without GitHub Action.
summarised_stars_df <- stars_df %>% 
  group_by(StarGroup, StarSubgroup) %>% 
  summarise(Count = n(), 
            WithoutWorkflows = sum(workflow_ga == 0), 
            WithWorkflow     = sum(workflow_ga > 0),
            MaxStars = max(stargazers),
            MinStars = min(stargazers),
            Stars = factor(paste(MinStars,"-",MaxStars))) %>% 
  mutate(PercAdoption = round(100*WithWorkflow/Count,1)) %>% 
  arrange(Stars)

# Create the bar plot with discretised groups of projects with star values.
stars_plot <- ggplot(summarised_stars_df, aes(x = reorder(Stars, MaxStars), y = PercAdoption, fill = StarGroup)) +
  geom_col(width = 0.8) +
  geom_hline(yintercept = 50, linetype = "dashed") +
  scale_fill_manual(values = my_palette) +
  scale_y_continuous(breaks = seq(0,100,by=20), limits = c(0,100)) +
  labs(y = "Perc. of GA Adoption", x = "Num. of Stars Per Sub-group") +
  theme_bw() + theme(text=element_text(size=15), axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1), legend.position = "none")

# Create the figure used in the paper.
ggsave(stars_plot, filename = "./figs/StarsPlot.pdf",device = cairo_pdf(), width = 25, height = 12, units = "cm")

# RQ1: Analysis of Contributors
# Create a discretized data frame with information of the contributors per project.
contributors_df <- raw_data_df %>% 
  arrange(contributors) %>% 
  mutate(ContribGroup = factor((floor(row_number()/1000))),
         ContribSubgroup = factor((floor(row_number()/200))))

# Summarise the information from all projects to compare projects with and
#.  without GitHub Action.
summarised_contrib_df <- contributors_df %>% 
  group_by(ContribGroup, ContribSubgroup) %>% 
  summarise(Count = n(), 
            WithoutWorkflows = sum(workflow_ga == 0), 
            WithWorkflow     = sum(workflow_ga > 0),
            MaxContrib = factor(max(contributors))) %>% 
  mutate(PercAdoption = round(100*WithWorkflow/Count,1))

# Create the bar plot with discretised groups of projects with contributors values.
contrib_plot <- ggplot(summarised_contrib_df, aes(x = MaxContrib, y = PercAdoption, fill = ContribGroup)) +
  geom_col(width = 0.8) +
  geom_hline(yintercept = 50, linetype = "dashed") +
  scale_fill_manual(values = my_palette) +
  scale_y_continuous(breaks = seq(0,100,by=20), limits = c(0,100)) +
  labs(y = "Perc. of GA Adoption", x = "Num. of Contributors Per Sub-group") +
  theme_bw() + theme(text=element_text(size=15), axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1), legend.position = "none")

# Create the figure used in the paper.
ggsave(contrib_plot, filename = "./figs/ContributorPlot.pdf",device = cairo_pdf(), width = 25, height = 12, units = "cm")


# Statistical Analysis for Mann-Whitney and Cliff's delta.
# RQ1: Comparison of projects
# Table 1: Descriptive statistics comparing projects with and without GitHub Actions.
attributes_df <- raw_data_df %>% 
  mutate(Group = ifelse(workflow_ga == 0, "Without", "With")) %>% 
  select(Group, 
         "Pull.Requests" = totalPullRequests, "Contributors" = contributors, 
         "Commits" = commits, "Issues" = totalIssues, "Stars" = stargazers, "Forks" = forks, "Watchers" = watchers) %>% 
  gather(key = "Variable", value = "Value", -Group)

summ_attr_df <- attributes_df %>% 
  group_by(Variable, Group) %>% 
  summarise(Median = median(Value), Avg = round(mean(Value),1),
            SD = round(sd(Value),1))

# Creates the table with all p-valus and deltas for the effect size.
p_df <- data.frame()
variables <- unique(attributes_df$Variable)
for(variable in variables) {
  print(paste("Calculating p-value for ", variable))
  temp <- attributes_df %>% filter(Variable == variable)
  p <- wilcox.test(Value ~ Group, data = temp)$p.value
  c.delta <- cliff.delta(Value ~ Group, data = temp)
  
  row <- data.frame("Variable" = variable, "P.Value" = p, 
                    "Cliff.Delta" = c.delta$estimate, "Eff.Size" = c.delta$magnitude)
  print(row)
  p_df <- bind_rows(p_df, row)
}

# Applies the Bonferroni correction to the p-values.
p_df <- p_df %>% 
  mutate(Adj.P.Value = p.adjust(P.Value, method = "bonferroni"))

# Creates Table 1 shown in the paper with descriptive statistics and results from
#.  the statistical tests.
table_df <- summ_attr_df %>% 
  select(Variable, Group, Median) %>% 
  pivot_wider(names_from = Group,
              names_sep = ".", 
              values_from = Median) %>% 
  left_join(., p_df, by = "Variable")

# Writes the table as a csv file
write.csv(table_df, file = "./data/output/table_statistics.csv")