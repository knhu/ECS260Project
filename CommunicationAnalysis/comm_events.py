import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import timedelta
import networkx as nx

# Load the CSV file
df = pd.read_csv('communication_events.csv')

# Clean the data
# Parse timestamps with timezone awareness
df['time1'] = pd.to_datetime(df['time1'], utc=True)
df['time2'] = pd.to_datetime(df['time2'], utc=True)

# Remove duplicates based on all columns
df_cleaned = df.drop_duplicates()

# Remove rows with missing critical data
df_cleaned = df_cleaned.dropna(subset=['author1', 'author2', 'time1', 'time2'])

# --- Data Analysis ---
# Total communication events
total_events = len(df_cleaned)
print(f"Communication Events, Total: {total_events}")

# Communication pairs (all pairs, not just top 10)
df_cleaned['author_pair'] = df_cleaned.apply(lambda row: tuple(sorted([row['author1'], row['author2']])), axis=1)
pair_counts = df_cleaned.groupby('author_pair').size().reset_index(name='events')
pair_counts = pair_counts.sort_values('events', ascending=False)

# Convert author_pair tuples to strings for plotting
pair_counts['author_pair_str'] = pair_counts['author_pair'].apply(lambda x: f"{x[0]},{x[1]}")

# Print top 10 pairs for reference
top_pairs = pair_counts.head(10)
print("\nTop 10 Communication Pairs:")
print(top_pairs[['author_pair_str', 'events']])

# Average time difference between time1 and time2
df_cleaned['time_diff'] = (df_cleaned['time2'] - df_cleaned['time1']).dt.total_seconds() / 3600  # Convert to hours
avg_time_diff = df_cleaned['time_diff'].mean()
print(f"\nAverage time difference between events: {avg_time_diff:.2f} hours")

# Communication events per file
file_events = df_cleaned.groupby('file').size().reset_index(name='event_count')
top_files = file_events.sort_values('event_count', ascending=False).head(10)

# --- Data Visualization ---
# 1. Bar Chart: Top 20 Author Pairs (for clarity, but calculate for all)
plt.figure(figsize=(14, 8))
sns.barplot(x='author_pair_str', y='events', data=pair_counts.head(20))  # Top 20 for readability
plt.xticks(rotation=45, ha='right')
plt.title('Top 20 Communication Pairs by Number of Events')
plt.xlabel('Author Pair')
plt.ylabel('Number of Events')
plt.tight_layout()
plt.show()

# 2. Histogram: Distribution of Communication Events per File
plt.figure(figsize=(10, 6))
sns.histplot(file_events['event_count'], bins=30, kde=True)
plt.title('Distribution of Communication Events per File')
plt.xlabel('Number of Events')
plt.ylabel('Frequency')
plt.show()

# 3. Histogram: Time Difference between Events
plt.figure(figsize=(10, 6))
sns.histplot(df_cleaned['time_diff'], bins=50, kde=True)
plt.title('Distribution of Time Differences Between Communication Events')
plt.xlabel('Time Difference (hours)')
plt.ylabel('Frequency')
plt.xlim(0, 48)  # Limit to 48 hours for clarity
plt.show()

# 4. Network Graph: Communication Network (all pairs, but visualize top for clarity)
G = nx.Graph()
for _, row in pair_counts.iterrows():
    pair = row['author_pair']
    G.add_edge(pair[0], pair[1], weight=row['events'])

plt.figure(figsize=(15, 10))
pos = nx.spring_layout(G)
# Draw only edges with significant weight (e.g., events >= 50) for clarity
edges_to_draw = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] >= 50]
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, edgelist=edges_to_draw, width=[G[u][v]['weight']/100 for u, v in edges_to_draw])
edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True) if d['weight'] >= 50}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title('Communication Network (Edges with >= 50 Events)')
plt.show()

# 5. Time Series: Communication Events Over Time (by month)
df_cleaned['month'] = df_cleaned['time1'].dt.to_period('M').astype(str)  # Convert to string to avoid TypeError
time_series = df_cleaned.groupby('month').size().reset_index(name='event_count')
plt.figure(figsize=(14, 6))
sns.lineplot(x='month', y='event_count', data=time_series)
plt.xticks(rotation=45)
plt.title('Communication Events Over Time (Monthly)')
plt.xlabel('Month')
plt.ylabel('Number of Events')
plt.tight_layout()
plt.show()