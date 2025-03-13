library(ggplot2)

dd <- read.csv("mergedFinalRemovedLowCommits.csv", header = TRUE)

ggplot(dd, aes(x = Sentiment, y = log(Code_Churn))) +
  geom_boxplot(fill = "lightblue", alpha = 0.6) +
  labs(title = "Code Churn by Sentiment Category", 
       x = "Sentiment", y = "Log(Code Churn)") +
  theme_minimal()

dd$Commit_Date <- as.Date(dd$Commit_Date)

dd$YearMonth <- format(dd$Commit_Date, "%Y-%m")

monthly_commits <- aggregate(Total_Commits ~ YearMonth, data = dd, sum)

ggplot(monthly_commits, aes(x = as.Date(paste0(YearMonth, "-01")), y = Total_Commits)) +
  geom_line(color = "blue", size = 1) +
  labs(title = "Total Commits Over Time", x = "Month", y = "Total Commits") +
  theme_minimal()