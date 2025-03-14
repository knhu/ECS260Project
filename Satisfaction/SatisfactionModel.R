library(car)
library(lme4)

finalModel <- lmer(log(Total.Commits) ~ Project.Age..Years. + (1|Author) + Negative.Commit.Percentage, data = finalRemovedLowCommits)
summary(finalModel)
vif(finalModel) 
plot(finalModel)
anova(finalModel)
