file <- "efficiency_data.csv"

data <- read.csv(file)

Churn_Q1 <- quantile(data$Average_Daily_Code_Churn, 0.25)
Churn_Q3 <- quantile(data$Average_Daily_Code_Churn, 0.75)
Churn_IQR <- IQR(data$Average_Daily_Code_Churn)

Commits_Q1 <- quantile(data$Average_Daily_Num_Commits, 0.25)
Commits_Q3 <- quantile(data$Average_Daily_Num_Commits, 0.75)
Commits_IQR <- IQR(data$Average_Daily_Num_Commits)

Commit_Time_Q1 <- quantile(data$Mean_Commit_Time, 0.25)
Commit_Time_Q3 <- quantile(data$Mean_Commit_Time, 0.75)
Commit_Time_IQR <- IQR(data$Mean_Commit_Time)
Commits <- data$Total_Commits
#Removing Churn outliers from dataset


data <- subset(data, data$Average_Daily_Code_Churn > 
                  (Churn_Q1 - 1.5*Churn_IQR) & data$Average_Daily_Code_Churn
                < (Churn_Q3 + 1.5*Churn_IQR))
#Removing Avg daily commits outlierss
#data <- subset(data, data$Average_Daily_Num_Commits > (Commits_Q1 - 1.5*Commits_IQR) & data$Average_Daily_Num_Commits
#               < (Commits_Q3 + 1.5*Commits_IQR))

#data <- subset(data, data$Mean_Commit_Time > (Commit_Time_Q1 - 1.5*Commit_Time_IQR) & data$Mean_Commit_Time
#               < (Commit_Time_Q3 + 1.5*Commit_Time_IQR))

Churn <- data$Average_Daily_Code_Churn
Commits <- data$Total_Commits
Daily_Commits <- data$Average_Daily_Num_Commits
Mean_Commit_Time <- data$Mean_Commit_Time
hist(Mean_Commit_Time)
hist(Commits)
hist(Churn)
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

