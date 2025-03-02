import pandas as pd

def deduplicate_author_project(input_csv, output_csv):
    """
    Reads a CSV, deduplicates author-project pairs, and saves to a new CSV.

    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file.
    """

    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Input CSV file '{input_csv}' not found.")
        return

    # Create a unique identifier for each author-project pair
    df['author_project'] = df['Author'] + '_' + df['Project Name']

    # Drop duplicates and remove the extra column
    deduplicated_df = df.drop_duplicates(subset='author_project', keep='first')
    deduplicated_df = deduplicated_df.drop(columns=['author_project'])

    # Save the deduplicated DataFrame to a new CSV file
    deduplicated_df.to_csv(output_csv, index=False)

    print(f"Deduplicated data saved to '{output_csv}'")


input_csv_file = 'commit_data_with_negative_percentage.csv'
output_csv_file = 'deduplicatedcommit_data_with_negative_percentage.csv'

deduplicate_author_project(input_csv_file, output_csv_file)