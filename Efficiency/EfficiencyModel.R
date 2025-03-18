library(nlcor)
library("ggpubr")
library(ggplot2)
library(gridExtra)
file <- "all_repos_efficiency.csv"

data <- read.csv(file)

#IQR Measurements for Churn, Avg daily commits, avg commit time
Churn_Q1 <- quantile(data$Average_Daily_Code_Churn, 0.25)
Churn_Q3 <- quantile(data$Average_Daily_Code_Churn, 0.75)
Churn_IQR <- IQR(data$Average_Daily_Code_Churn)

Commits_Q1 <- quantile(data$Average_Daily_Num_Commits, 0.25)
Commits_Q3 <- quantile(data$Average_Daily_Num_Commits, 0.75)
Commits_IQR <- IQR(data$Average_Daily_Num_Commits)

Commit_Time_Q1 <- quantile(data$Mean_Commit_Time, 0.25)
Commit_Time_Q3 <- quantile(data$Mean_Commit_Time, 0.75)
Commit_Time_IQR <- IQR(data$Mean_Commit_Time)

Total_Commits_Q1 <- quantile(data$Total_Commits, 0.25)
Total_Commits_Q3 <- quantile(data$Total_Commits, 0.75)
Total_Commits_IQR <- IQR(data$Total_Commits)

Total_Churn_Q1 <- quantile(data$Total_Code_Churn, 0.25)
Total_Churn_Q3 <- quantile(data$Total_Code_Churn, 0.75)
Total_Churn_IQR <- IQR(data$Total_Code_Churn)

Commits <- data$Total_Commits
#Removing Churn outliers from dataset


data <- subset(data, data$Average_Daily_Code_Churn > 
                  (Churn_Q1 - 1.5*Churn_IQR) & data$Average_Daily_Code_Churn
                < (Churn_Q3 + 1.5*Churn_IQR))
#Removing Avg daily commits outlierss
data <- subset(data, data$Average_Daily_Num_Commits > (Commits_Q1 - 1.5*Commits_IQR) & data$Average_Daily_Num_Commits
               < (Commits_Q3 + 1.5*Commits_IQR))

data <- subset(data, data$Mean_Commit_Time > (Commit_Time_Q1 - 1.5*Commit_Time_IQR) & data$Mean_Commit_Time
               < (Commit_Time_Q3 + 1.5*Commit_Time_IQR))

data <- subset(data, data$Total_Commits > (Total_Commits_Q1 - 1.5*Total_Commits_IQR) & data$Total_Commits
               < (Total_Commits_Q3 + 1.5*Total_Commits_IQR))

data <- subset(data, data$Total_Code_Churn > (Total_Churn_Q1 - 1.5*Total_Churn_IQR) & data$Total_Code_Churn
               < (Total_Commits_Q3 + 1.5*Total_Churn_IQR))
AVG_Daily_Churn <- data$Average_Daily_Code_Churn
Total_Churn <- data$Total_Code_Churn
Commits <- data$Total_Commits
Daily_Commits <- data$Average_Daily_Num_Commits
Mean_Commit_Time <- data$Mean_Commit_Time
hist(Mean_Commit_Time)
hist(Commits)
hist(Churn)
hist(Total_Churn)
mean(Churn)
median(Churn)
boxplot(Churn)
hist(Daily_Commits)
title("Average Daily Commits vs Average Daily Code Churn")
plot(Daily_Commits,Churn, 
     xlab="Average Daily Commits",ylab="Average Daily Code Churn",
     pch=19, col = "black",) #Average daily commits vs average daily churn
plot(Commits,Churn)

plot(Daily_Commits,Mean_Commit_Time)
plot(Commits,Mean_Commit_Time)
plot(Mean_Commit_Time,Churn)

#Correlation Tests

cor(data[,c('Mean_Commit_Time','Total_Commits','Average_Daily_Num_Commits','Total_Code_Churn','Average_Daily_Code_Churn')])

cor.test(Mean_Commit_Time,Commits)
cor.test(Mean_Commit_Time,Daily_Commits)
cor.test(Mean_Commit_Time,Total_Churn)
cor.test(Mean_Commit_Time,AVG_Daily_Churn)

cor.test(Commits,Daily_Commits)
cor.test(Commits,Total_Churn)
cor.test(Commits,AVG_Daily_Churn)

cor.test(Daily_Commits,Total_Churn)
cor.test(Daily_Commits,AVG_Daily_Churn)

cor.test(Total_Churn,AVG_Daily_Churn)

cor.test()

m<-nls(Mean_Commit_Time ~ (Commits-20)^(-1/2), start= list(Commits=21))

nlcor(Mean_Commit_Time,Commits, plt= T)
nlcor(Commits,Mean_Commit_Time, plt= T)

cor.test(Commits,Total_Churn, method=c("pearson","kendall","spearman"))

plot(log(Commits),log(Total_Churn))

g1 <- ggscatter(data, x = "Total_Commits", y = "Total_Code_Churn", xlab="Total Commits", ylab = "Total Code Churn",size=1,
          add = "reg.line", conf.int = TRUE, cor.coef = TRUE, cor.method = "pearson",
          title="Total Commits vs. Total Code Churn") + theme(plot.title = element_text(hjust=0.5))

g2 <- ggscatter(data, x = "Mean_Commit_Time", y = "Total_Code_Churn", xlab="Mean Daily Commit Time (Minutes)", ylab = "Total Code Churn",size=1,
                add = "reg.line", conf.int = TRUE, cor.coef = TRUE, cor.method = "pearson",
                title="Mean Daily Commit Time vs. Total Code Churn") + theme(plot.title = element_text(hjust=0.5))

g3 <- ggscatter(data, x = "Average_Daily_Num_Commits", y = "Average_Daily_Code_Churn", xlab="Average Daily Commits", ylab = "Average Daily Code Churn",size=1,
                add = "reg.line", conf.int = TRUE, cor.coef = TRUE, cor.method = "pearson",
                title="Average daily Commits vs Average Daily Code Churn") + theme(plot.title = element_text(hjust=0.5))

grid.arrange(g1,g2,g3)
