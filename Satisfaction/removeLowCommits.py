import pandas as pd

def remove_rows_with_low_commits(input_file, output_file, threshold=20):
    """
    Reads a CSV file using pandas, removes rows where the 'Total Commits' 
    column is less than or equal to a threshold, and writes the filtered 
    data to a new CSV file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
        threshold (int): The threshold value for 'Total Commits'. 
                         Rows with values less than or equal to this 
                         will be removed. Default is 20.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Filter out low commit authors
        df_filtered = df[df['Total Commits'] > threshold]

        # Write to new CSV
        df_filtered.to_csv(output_file, index=False)

        print(f"Successfully filtered '{input_file}' and saved to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except KeyError:
        print(f"Error: Column 'Total Commits' not found in the CSV file.")
    except Exception as e:
        print(f"An error occurred: {e}")


input_csv = 'deduplicatedcommit_data_with_negative_percentage.csv' 
output_csv = 'finalRemovedLowCommits.csv'
remove_rows_with_low_commits(input_csv, output_csv)