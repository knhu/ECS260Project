# =====================================================
# Confirmatory Analysis for Performance Dimension
# - with manual partial correlation (no ppcor).
# =====================================================

# 0. Load Required Libraries
# install.packages("readr")
# install.packages("dplyr")
library(readr)
library(dplyr)

# 1. Repository-level Data
repo_data <- read_csv("cleaned_repo_performance.csv")

cat("=== REPO DATA: Basic Summary ===\n")
summary(repo_data)

# Example multiple regression controlling for total_commits
repo_model <- lm(avg_pr_merge_time ~ ci_cd_success_rate + total_commits, data = repo_data)
cat("\n=== Multiple Regression (Repo) ===\n")
summary(repo_model)

# Manual partial correlation:
# We want partial correlation between X=avg_pr_merge_time and Y=ci_cd_success_rate
# controlling for Z=total_commits
# 1) Regress X~Z => get residuals Xres
# 2) Regress Y~Z => get residuals Yres
# 3) cor(Xres, Yres)

# A) Make sure no missing data
repo_subset <- repo_data %>%
  select(avg_pr_merge_time, ci_cd_success_rate, total_commits) %>%
  na.omit()

# B) Residuals
repo_mod_X <- lm(avg_pr_merge_time ~ total_commits, data = repo_subset)
Xres <- repo_mod_X$residuals

repo_mod_Y <- lm(ci_cd_success_rate ~ total_commits, data = repo_subset)
Yres <- repo_mod_Y$residuals

# C) Correlation test on residuals
repo_partial_cor <- cor.test(Xres, Yres, method="pearson")
cat("\n=== Partial Correlation (Repo) for avg_pr_merge_time & ci_cd_success_rate controlling total_commits ===\n")
print(repo_partial_cor)

# 2. Contributor-level Data
contrib_data <- read_csv("cleaned_contributor_performance.csv")

cat("\n=== CONTRIBUTOR DATA: Basic Summary ===\n")
summary(contrib_data)

# Single regression examples:
model_contrib_a <- lm(code_churn ~ total_commits, data = contrib_data)
cat("\n=== Model A: code_churn ~ total_commits ===\n")
summary(model_contrib_a)

model_contrib_b <- lm(code_churn ~ bug_fix_commits, data = contrib_data)
cat("\n=== Model B: code_churn ~ bug_fix_commits ===\n")
summary(model_contrib_b)

# Manual partial correlation:
# X=code_churn, Y=bug_fix_commits, controlling Z=total_commits
# 1) X~Z => Xres
# 2) Y~Z => Yres
# 3) cor(Xres, Yres)

contrib_subset <- contrib_data %>%
  select(code_churn, bug_fix_commits, total_commits) %>%
  na.omit()

# A) Xres = code_churn - effect of total_commits
modelX <- lm(code_churn ~ total_commits, data = contrib_subset)
Xres <- modelX$residuals

# B) Yres = bug_fix_commits - effect of total_commits
modelY <- lm(bug_fix_commits ~ total_commits, data = contrib_subset)
Yres <- modelY$residuals

# C) Partial correlation
contrib_partial_cor <- cor.test(Xres, Yres, method="pearson")
cat("\n=== Partial Correlation (Contrib) for code_churn & bug_fix_commits controlling total_commits ===\n")
print(contrib_partial_cor)

cat("\n=== Confirmatory Analysis with Manual Partial Correlations Complete. ===\n")
