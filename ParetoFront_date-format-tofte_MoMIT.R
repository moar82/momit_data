require(scatterplot3d)

rm(list = ls())
setwd("/home/moar82/gitrepos/momit_data")

PATH = "/home/moar82/Documents/iot_miniaturization/results/sunspider/pf_250_evals_raw/date-format-tofte.pf"
OUTPUT = "ParetoFront_date-format-tofte_MoMIT.pdf"


data = read.csv(PATH)

data$cs<-data$V1/1000
data$mu<-data$V2/1000

data[1:2]<-NULL
data[1]<-NULL
data[2]<-NULL



attach(data)

pdf(OUTPUT,height = 8.5, width =11)

scatterplot3d(cs, mu, V3,
              color="red",
              pch=16,
              type="h",
              main="Pareto Front of date-format-tofte after miniaturization",
              xlab="Code Size in KB",
              ylab="Memory usage KB",
              zlab="Execution Time Seconds",
              ylim=c(80,27000),
              cex.axis=1.1,
              cex.lab = 1.1)
dev.off()

detach(data)
summary(data)

table(cs,mu)

table (data$mu<128)