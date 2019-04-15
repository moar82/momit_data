#!/usr/bin/env Rscript
rm(list = ls())
setwd("/home/moar82/gitrepos/momit_data")


PATH = "median_improvements_merged.csv"
OUTPUT = "PerformanceImprovement_MoMIT.pdf"

data = read.csv(PATH)
data <-data[!(data$JS.test=="Total Median"), ]

library(scatterplot3d)
# attach(mtcars)
# scatterplot3d(wt, disp, mpg,
#               pch=16,
#               highlight.3d=TRUE,
#               type="h",
#               main="3D Scatter Plot with Vertical Lines")
# 
# scatterplot3d(wt, disp, mpg,
#               main="Basic 3D Scatter Plot")
# 
# detach(mtcars)

attach(data)

scatterplot3d(delta_CSp, delta_MUp, delta_etp,
              pch=16,
              highlight.3d=TRUE,
              type="h",
              main="Basic 3D Scatter Plot")


require(ggplot2)

ggplot(data, aes(delta_CSp, delta_MUp, delta_etp)) + geom_point() + geom_text(aes(label=JS.test))

data$delta_CSp<-delta_CS*-1
data$delta_MUp<-delta_MU*-1
data$delta_etp<-delta_et*-1
require(grDevices)
require(stats)

r <- sqrt(delta_etp/pi)
symbols(delta_CSp, delta_MUp, circle=r, inches=0.30,
        fg="white", bg="lightblue",
        main="Bubble Plot with point size proportional to execution time improvement",
        ylab="Memory usage Improvement",
        xlab="Code size improvement")
text(delta_CSp, delta_MUp, JS.test, cex=0.6)

data <-data[!(data$JS.test=="bitops-3bit-bits-in-byte" ), ]
data <-data[!(data$JS.test=="crypto-aes" ), ]

pdf("thermoteter.pdf",height = 8.5, width =11)
symbols(delta_CSp, delta_MUp, thermometers = cbind(.5, 1, delta_etp/100), inches = .5, fg = 2,
        main="Thermometer Plot with fill proportional to execution time improvement",
        ylab="Memory usage Improvement (%)",
        xlab="Code size improvement (%)")
text(delta_CSp, delta_MUp, JS.test, cex=0.6) #ommit if you do not want to show the name of the systems
dev.off()



symbols(delta_CSp, delta_MUp, thermometers = delta_etp, inches = FALSE)
text(delta_CSp, delta_MUp, apply(format(round(delta_etp, digits = 2)), 1, paste, collapse = ","),
     adj = c(-.2,0), cex = .75, col = "purple", xpd = NA)


p	
ggsave(p, file = OUTPUT, width = 12, height = 6, useDingbats = FALSE)