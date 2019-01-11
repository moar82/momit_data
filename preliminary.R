library("dplyr")
library("magrittr")
#setwd("c:/Users/moar82/Documents/momit/")
setwd("~/gitrepos/momit_data/")
df<-read.csv("results_benchmark_primeSimple_clean.csv")

df_group<-df %>%
  group_by(id,value,feature_size,mem_us,size_delta,mem_delta,) %>%
  summarize(median(time_usr), median(time_delta)) 

summary(df_group)

colnames(df)
pdf("boxplot_prelim.pdf",height = 8.5, width =11)

boxplot(df_group$size_delta,df_group$mem_delta,df_group$`median(time_delta)`,
        names = c('File size','Memory usage', 'Execution time'))
dev.off()

coef_var_file_size<- sd(df_group$size_delta)/mean(df_group$size_delta)
coef_var_mem_us<- sd(df_group$mem_delta)/mean(df_group$mem_delta)
coef_var_exec_time<- sd(df_group$`median(time_delta)`)/mean(df_group$`median(time_delta)`)

coef_var_metrics<- c(coef_var_file_size,coef_var_mem_us,coef_var_exec_time)

for (coef in  coef_var_metrics) print (coef)

# let's remove the outlier of time delta to observe more detail on the time_delta boxplot.

time_delta<-df_group$`median(time_delta)`[df_group$`median(time_delta)`<0]


boxplot(df_group$size_delta,df_group$mem_delta,time_delta,
        names = c('File size','Memory usage', 'Execution time'))

mem_delta_f<-df_group$mem_delta[df_group$mem_delta>-30]

boxplot(df_group$size_delta,mem_delta_f,time_delta,
        names = c('File size','Memory usage', 'Execution time'))


outvals_file_size<-boxplot(df_group$size_delta,
                 plot=F)$out
which(df_group$size_delta %in% outvals)

length (df_group$size_delta[df_group$size_delta!=0])

length (df_group$mem_delta[df_group$mem_delta!=0])

length (df_group$`median(time_delta)`[df_group$`median(time_delta)`!=0])


outvals_mem_us<-boxplot(df_group$mem_delta,
                 plot=F)$out

df_noimpact<- df_group[which (df_group$size_delta==0 & df_group$mem_delta==0 &
                                df_group$`median(time_delta)`==0),]

df_gth5<-df_group[which (df_group$size_delta>=5 | df_group$mem_delta>=5 |
                  df_group$`median(time_delta)`>=5),]

df_lth5<-df_group[which (df_group$size_delta<=-10 | df_group$mem_delta<=-10 |
                  df_group$`median(time_delta)`<=-10),]

df_major_concern<-merge(df_lth5,df_gth5)

#probably it is better to select different threshold for
#time delta, since the median is ~-11
# I suggest to use the outliers for that purpose




