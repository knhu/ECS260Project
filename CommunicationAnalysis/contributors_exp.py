import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, probplot  # Import both shapiro and probplot from scipy.stats
import numpy as np

# Load the CSV file
df = pd.read_csv('contributors_experience (2).csv')

# Clean the data: Remove rows where "Top Contributor Share (%)" == 100.00 (if any)
df_cleaned = df[df['Top Contributor Share (%)'] != 100.00].copy()

# --- Data Analysis ---
# Calculate descriptive statistics
stats = df_cleaned['Top Contributor Share (%)'].describe()
median = df_cleaned['Top Contributor Share (%)'].median()
print("Descriptive Statistics:")
print(stats)
print(f"Median: {median}")

# Perform Shapiro-Wilk test for normality (convert Series to NumPy array)
# Note: For large datasets (>5000), Shapiro-Wilk may be unreliable due to power
try:
    stat, p_value = shapiro(df_cleaned['Top Contributor Share (%)'].values)
    print(f"\nShapiro-Wilk Test: statistic={stat}, p-value={p_value}")
    if p_value > 0.05:
        print("The data appears to be normally distributed (p > 0.05)")
    else:
        print("The data does not appear to be normally distributed (p <= 0.05)")
except ValueError as e:
    print(f"\nShapiro-Wilk Test failed: {e}. This may be due to the large sample size (>5000). Consider a visual check instead.")

# Categorize into Low (0-33%), Medium (33-66%), High (66-100%)
bins = [0, 33, 66, 100]
labels = ['Low (0-33%)', 'Medium (33-66%)', 'High (66-100%)']
df_cleaned['Category'] = pd.cut(df_cleaned['Top Contributor Share (%)'], 
                                bins=bins, labels=labels, include_lowest=True)
category_counts = df_cleaned['Category'].value_counts().sort_index()

# Calculate proportion of files with top contributor share < 50%
balanced_files = df_cleaned[df_cleaned['Top Contributor Share (%)'] < 50]
proportion_balanced = len(balanced_files) / len(df_cleaned)
print(f"\nProportion of files with top contributor share < 50%: {proportion_balanced:.2f}")

# --- Data Visualization ---
# 1. Histogram with KDE
plt.figure(figsize=(10, 6))
sns.histplot(df_cleaned['Top Contributor Share (%)'], bins=20, kde=True)
plt.title('Distribution of Top Contributor Share (%) After Cleaning')
plt.xlabel('Top Contributor Share (%)')
plt.ylabel('Frequency')
plt.show()

# 2. Box plot
plt.figure(figsize=(8, 6))
sns.boxplot(y='Top Contributor Share (%)', data=df_cleaned)
plt.title('Box Plot of Top Contributor Share (%) After Cleaning')
plt.ylabel('Top Contributor Share (%)')
plt.show()

# 3. Bar chart of categories
plt.figure(figsize=(8, 6))
category_counts.plot(kind='bar')
plt.title('Number of Files by Top Contributor Share Category')
plt.xlabel('Category')
plt.ylabel('Number of Files')
plt.xticks(rotation=0)
plt.show()

# 4. Q-Q plot for normality check (using scipy.stats.probplot)
plt.figure(figsize=(8, 6))
probplot(df_cleaned['Top Contributor Share (%)'].values, dist="norm", plot=plt)  # Correct usage
plt.title('Q-Q Plot of Top Contributor Share (%)')
plt.xlabel('Theoretical Quantiles')
plt.ylabel('Sample Quantiles')
plt.show()

# Print category counts and percentages
print("\nCategory Counts:")
for category in labels:
    count = category_counts.get(category, 0)
    percentage = (count / len(df_cleaned)) * 100
    print(f"{category}: {count} files ({percentage:.2f}%)")