library(car)
library(lme4)

# Read the file
dd = read.csv("all_mined_repos_cleaned.csv",header=T,sep=",")

# exploratory analysis
boxplot(log(abs(dd$Code.Churn) + 1))

# Simple Regression
model1 = lm(log(abs(dd$Code.Churn) + 1) ~ dd$Total.Commits)
summary(model1)
vif(model1)
par(mfrow = c(2, 2))
plot(model1)
anova(model1)

# Model 2: Predicting Code Churn with Total Commits and Avg Complexity - good model
model2 = lm(log(abs(dd$Code.Churn) + 1) ~ log(dd$Total.Commits + 1) + log(dd$Avg.Complexity + 1))
summary(model2)
vif(model2)
par(mfrow = c(2, 2))
plot(model2)
anova(model2)

# Best Model so far
model3 = lm(log(abs(dd$Code.Churn) + 1) ~ log(dd$Total.Commits + 1) + log(dd$Avg.Complexity + 1) + dd$Total.Code.Reviews * dd$Total.Deployments)
summary(model3)
par(mfrow = c(2, 2))
plot(model3)
