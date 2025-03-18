# =====================================================
# Exploratory Data Analysis (EDA) in R 4.4.3
# =====================================================
# We'll analyze:
# 1) CI/CD Success Rate vs. Average PR Merge Time (repo-level)
# 2) Total Commits vs. Code Churn (contributor-level)
# 3) Bug Fix Commits vs. Code Churn (contributor-level)
# 
# With optional enhancements:
#   - Log transform for avg_pr_merge_time
#   - Logit transform for ci_cd_success_rate
#   - Mild outlier removal (winsorizing) for avg_pr_merge_time
#
# 0. Load Required Libraries
# install.packages("ggplot2")
# install.packages("dplyr")
# install.packages("readr")
# install.packages("ggpubr")

library(ggplot2)
library(dplyr)
library(readr)
library(ggpubr)

# Function to remove outliers in a numeric vector using IQR or percentile approach
remove_outliers <- function(vec, lower.quantile = 0.01, upper.quantile = 0.99) {
  lower <- quantile(vec, lower.quantile, na.rm=TRUE)
  upper <- quantile(vec, upper.quantile, na.rm=TRUE)
  pmin(pmax(vec, lower), upper)  # Winsorize
}

# =====================================================
# 1. Repository-Level Analysis
# =====================================================
analyze_repo_data <- function(
    repo_file = "cleaned_repo_performance.csv",
    do_log_merge_time = TRUE,   # Log transform avg_pr_merge_time + 1
    do_logit_success_rate = FALSE,  # Logit transform success rate
    do_outlier_merge_time = FALSE   # Winsorize merges (1st & 99th)
) {
  repo_data <- read_csv(repo_file)
  
  cat("=== Repository Data Summary (initial) ===\n")
  print(summary(repo_data))
  
  # Check for columns
  needed_cols <- c("repo_name", "ci_cd_success_rate", "avg_pr_merge_time")
  missing_cols <- setdiff(needed_cols, names(repo_data))
  if(length(missing_cols) > 0) {
    stop(paste("Missing columns in repo data:", paste(missing_cols, collapse=", ")))
  }
  
  # (Optional) Winsorize merges if do_outlier_merge_time
  if(do_outlier_merge_time) {
    cat("\n[INFO] Winsorizing 'avg_pr_merge_time' at 1st/99th percentile...\n")
    repo_data$avg_pr_merge_time <- remove_outliers(repo_data$avg_pr_merge_time)
  }
  
  # (Optional) Log transform merges
  if(do_log_merge_time) {
    cat("\n[INFO] Creating 'log_merge_time' = log(avg_pr_merge_time + 1)\n")
    repo_data$log_merge_time <- log(repo_data$avg_pr_merge_time + 1)
  }
  
  # (Optional) Logit transform CI/CD success rate
  # logit(x) = ln( x / (1-x) ), must ensure 0 < x < 1
  if(do_logit_success_rate) {
    cat("\n[INFO] Creating 'logit_success_rate' = log(ci_cd_success_rate / (1 - ci_cd_success_rate))\n")
    # Clip success_rate slightly to avoid logit(0) or logit(1)
    sr_clip <- pmin(pmax(repo_data$ci_cd_success_rate, 0.000001), 0.999999)
    repo_data$logit_success_rate <- log(sr_clip / (1 - sr_clip))
  }
  
  # 1A. Summary (post transformations)
  cat("=== Repository Data Summary (post transformations) ===\n")
  print(summary(repo_data))
  
  # Histograms
  ggplot(repo_data, aes(x = ci_cd_success_rate)) +
    geom_histogram(bins = 30, fill = "blue", alpha=0.7) +
    ggtitle("Histogram of CI/CD Success Rate") +
    xlab("CI/CD Success Rate") + ylab("Frequency")
  
  ggplot(repo_data, aes(x = avg_pr_merge_time)) +
    geom_histogram(bins = 30, fill = "green", alpha=0.7) +
    ggtitle("Histogram of (Possibly Winsorized) Avg PR Merge Time") +
    xlab("Avg PR Merge Time (hours)") + ylab("Frequency")
  
  if(do_log_merge_time) {
    ggplot(repo_data, aes(x = log_merge_time)) +
      geom_histogram(bins = 30, fill = "red", alpha=0.7) +
      ggtitle("Histogram of log(Avg PR Merge Time + 1)") +
      xlab("log_merge_time") + ylab("Frequency")
  }
  
  # (A) Scatter (raw success rate vs. raw merges)
  cat("\n=== Scatter: CI/CD Success Rate vs. (Possibly Winsorized) Avg PR Merge Time ===\n")
  ggplot(repo_data, aes(x = ci_cd_success_rate, y = avg_pr_merge_time)) +
    geom_point(alpha = 0.6, color = "red") +
    geom_smooth(method = "lm", se=FALSE, color = "black") +
    ggtitle("CI/CD Success Rate vs. Avg PR Merge Time (raw)") +
    xlab("CI/CD Success Rate") + ylab("Avg PR Merge Time (hrs)")
  
  cor_raw <- cor.test(repo_data$ci_cd_success_rate, repo_data$avg_pr_merge_time,
                      method = "pearson", use = "complete.obs")
  print(cor_raw)
  
  # (B) If log transform merges
  if(do_log_merge_time) {
    cat("\n=== Scatter: CI/CD Success Rate vs. log_merge_time ===\n")
    ggplot(repo_data, aes(x = ci_cd_success_rate, y = log_merge_time)) +
      geom_point(alpha = 0.6, color = "blue") +
      geom_smooth(method = "lm", se=FALSE, color = "black") +
      ggtitle("CI/CD Success Rate vs. log(Avg PR Merge Time + 1)") +
      xlab("CI/CD Success Rate") + ylab("log_merge_time")
    
    cor_log <- cor.test(repo_data$ci_cd_success_rate, repo_data$log_merge_time,
                        method = "pearson", use = "complete.obs")
    print(cor_log)
  }
  
  # (C) If logit transform success rate
  if(do_logit_success_rate) {
    cat("\n=== Scatter: logit_success_rate vs. avg_pr_merge_time ===\n")
    ggplot(repo_data, aes(x = logit_success_rate, y = avg_pr_merge_time)) +
      geom_point(alpha=0.6, color="darkgreen") +
      geom_smooth(method="lm", se=FALSE, color="black") +
      ggtitle("logit(CI/CD Success Rate) vs. Avg PR Merge Time") +
      xlab("logit_success_rate") + ylab("Avg PR Merge Time (hrs)")
    
    cor_logit_raw <- cor.test(repo_data$logit_success_rate, repo_data$avg_pr_merge_time,
                              method="pearson", use="complete.obs")
    print(cor_logit_raw)
  }
  
  cat("\n[Repo-level analysis complete.]\n")
}

# =====================================================
# 2. Contributor-Level Analysis
# =====================================================
analyze_contributor_data <- function(contrib_file="cleaned_contributor_performance.csv") {
  # This CSV is assumed to have columns:
  #  [ 'contributor', 'repo', 'total_commits', 'total_prs',
  #    'avg_pr_merge_time', 'code_churn', 'bug_fix_commits', ... ]
  
  contrib_data <- read_csv(contrib_file)
  
  cat("\n=== Contributor Data Summary ===\n")
  summary(contrib_data)
  
  # Dist checks
  ggplot(contrib_data, aes(x = total_commits)) +
    geom_histogram(bins = 30, fill = "orange", alpha=0.7) +
    ggtitle("Histogram of Total Commits") +
    xlab("Total Commits") +
    ylab("Frequency")
  
  ggplot(contrib_data, aes(x = code_churn)) +
    geom_histogram(bins = 30, fill = "purple", alpha=0.7) +
    ggtitle("Histogram of Code Churn") +
    xlab("Code Churn") +
    ylab("Frequency")
  
  ggplot(contrib_data, aes(x = bug_fix_commits)) +
    geom_histogram(bins = 30, fill = "steelblue", alpha=0.7) +
    ggtitle("Histogram of Bug Fix Commits") +
    xlab("Bug Fix Commits") +
    ylab("Frequency")
  
  # Relationship (a) total_commits vs. code_churn
  ggplot(contrib_data, aes(x = total_commits, y = code_churn)) +
    geom_point(alpha = 0.6, color = "blue") +
    geom_smooth(method = "lm", se = FALSE, color = "black") +
    ggtitle("Total Commits vs. Code Churn") +
    xlab("Total Commits") +
    ylab("Code Churn")
  
  cor_test_contrib_a <- cor.test(
    contrib_data$total_commits,
    contrib_data$code_churn,
    method = "pearson",
    use = "complete.obs"
  )
  cat("\nCorrelation Test (Contrib-level): Total Commits vs. Code Churn\n")
  print(cor_test_contrib_a)
  
  # Relationship (b) bug_fix_commits vs. code_churn
  ggplot(contrib_data, aes(x = bug_fix_commits, y = code_churn)) +
    geom_point(alpha = 0.6, color = "darkgreen") +
    geom_smooth(method = "lm", se = FALSE, color = "black") +
    ggtitle("Bug Fix Commits vs. Code Churn") +
    xlab("Bug Fix Commits") +
    ylab("Code Churn")
  
  cor_test_contrib_b <- cor.test(
    contrib_data$bug_fix_commits,
    contrib_data$code_churn,
    method = "pearson",
    use = "complete.obs"
  )
  cat("\nCorrelation Test (Contrib-level): Bug Fix Commits vs. Code Churn\n")
  print(cor_test_contrib_b)
  
  cat("\n[Contributor-level analysis complete.]\n")
}

# =====================================================
# 3. Main EDA Orchestrator
# =====================================================
# This function runs the repo-level & contributor-level analyses.
perform_EDA <- function(
    repo_file = "cleaned_repo_performance.csv",
    contrib_file = "cleaned_contributor_performance.csv",
    do_log_merge_time = TRUE,
    do_logit_success_rate = FALSE,
    do_outlier_merge_time = FALSE
) {
  cat("=== Starting EDA for Repo-level data ===\n")
  analyze_repo_data(
    repo_file = repo_file,
    do_log_merge_time = do_log_merge_time,
    do_logit_success_rate = do_logit_success_rate,
    do_outlier_merge_time = do_outlier_merge_time
  )
  
  cat("\n=== Starting EDA for Contributor-level data ===\n")
  analyze_contributor_data(contrib_file = contrib_file)
  
  cat("\n[Overall EDA complete.]\n")
}

# Example usage:
# perform_EDA(
#   repo_file = "cleaned_repo_performance.csv",
#   contrib_file = "cleaned_contributor_performance.csv",
#   do_log_merge_time = TRUE,
#   do_logit_success_rate = FALSE,
#   do_outlier_merge_time = TRUE
# )
