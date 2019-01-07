library("dplyr")
library("magrittr")
setwd("c:/Users/moar82/Documents/momit/")

df<-read.csv("c:/Users/moar82/Documents/momit/results_benchmark_primeSimple_clean.csv")

df_group<-df %>%
  group_by(id,value,feature_size,mem_us,size_delta,mem_delta,) %>%
  summarize(median(time_usr), median(time_delta)) 

summary(df_group)

colnames(df)