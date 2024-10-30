library(tidyverse)


my_palette <- c("#eae4e9","#fff1e6","#fde2e4","#fad2e1","#e2ece9","#bee1e6","#f0efeb","#dfe7fd","#cddafd")
my_palette <- c("#ffadad","#ffd6a5","#fdffb6","#caffbf","#9bf6ff","#a0c4ff","#bdb2ff","#ffc6ff","#fde2e4")
my_palette <- c("#303638","#f0c808","#5d4b20","#469374","#9341b3","#e3427d","#e68653","#ebe0b0","#edfbba")

raw_data_df <- read.csv("./analysis data/enriched_analysis.csv")

languages_df <- raw_data_df %>% 
  select(mainLanguage, workflow_ga) %>%
  group_by(mainLanguage) %>% 
  summarise(Count = n(), 
            WithoutWorkflows = sum(workflow_ga == 0), 
            WithWorkflow     = sum(workflow_ga > 0)) %>% 
  mutate(PercProjs    = round(100*Count/sum(Count)  ,1),
         PercAdoption = round(100*WithWorkflow/Count,1))

lang_plot <- ggplot(languages_df, aes(x = reorder(mainLanguage, -PercAdoption), y = PercAdoption, label = paste(PercProjs,"%"))) +
  geom_col(width = 0.8, fill = "#bcb6f6") +
  geom_hline(yintercept = 50, linetype = "dashed") +
  geom_text(aes(y = 5), vjust = -0.5, size = 3) +
  scale_y_continuous(breaks = seq(0,100,by=20), limits = c(0,100)) +
  labs(y = "Perc. of GA Adoption", x = "Programming Languages") +
  theme_bw() + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1), legend.position = "none")

ggsave(lang_plot, filename = "figs/LanguagePlot.pdf",
       device = cairo_pdf(), width = 25, height = 12, units = "cm")

## Stargazers

stars_df <- raw_data_df %>% 
  arrange(stargazers) %>% 
  mutate(StarGroup = factor((floor(row_number()/1000))),
         StarSubgroup = factor((floor(row_number()/200))))

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

stars_plot <- ggplot(summarised_stars_df, aes(x = reorder(Stars, MaxStars), y = PercAdoption, fill = StarGroup)) +
  geom_col(width = 0.8) +
  geom_hline(yintercept = 50, linetype = "dashed") +
  scale_fill_manual(values = my_palette) +
  scale_y_continuous(breaks = seq(0,100,by=20), limits = c(0,100)) +
  labs(y = "Perc. of GA Adoption", x = "Num. of Stars Per Sub-group") +
  theme_bw() + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1), legend.position = "none")

ggsave(stars_plot, filename = "figs/StarsPlot.pdf",
       device = cairo_pdf(), width = 25, height = 12, units = "cm")

## Contributors  

contributors_df <- raw_data_df %>% 
  arrange(contributors) %>% 
  mutate(ContribGroup = factor((floor(row_number()/1000))),
         ContribSubgroup = factor((floor(row_number()/200))))

summarised_contrib_df <- contributors_df %>% 
  group_by(ContribGroup, ContribSubgroup) %>% 
  summarise(Count = n(), 
            WithoutWorkflows = sum(workflow_ga == 0), 
            WithWorkflow     = sum(workflow_ga > 0),
            MaxContrib = factor(max(contributors))) %>% 
  mutate(PercAdoption = round(100*WithWorkflow/Count,1))

contrib_plot <- ggplot(summarised_contrib_df, aes(x = MaxContrib, y = PercAdoption, fill = ContribGroup)) +
  geom_col(width = 0.8) +
  geom_hline(yintercept = 50, linetype = "dashed") +
  scale_fill_manual(values = my_palette) +
  scale_y_continuous(breaks = seq(0,100,by=20), limits = c(0,100)) +
  labs(y = "Perc. of GA Adoption", x = "Num. of Contributors Per Sub-group") +
  theme_bw() + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1), legend.position = "none")

ggsave(contrib_plot, filename = "figs/ContributorPlot.pdf",
       device = cairo_pdf(), width = 25, height = 12, units = "cm")
