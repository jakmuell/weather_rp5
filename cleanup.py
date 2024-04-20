import pandas as pd

def filter_csv(input_file, output_file):

    with open(input_file, 'r', newline='') as infile:
        csv_content = infile.read()

    rows = csv_content.split('\n')
    non_comment_index = next((i for i, row in enumerate(rows) if not row.startswith('#')), len(rows))
    new_csv_content = '\n'.join(rows[non_comment_index:])

    with open(output_file, 'w', newline='') as outfile:
        outfile.write(new_csv_content)

def format_dataframe(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(output_file, sep=';', decimal='.', index_col=False)
    df = df.rename(columns={df.columns[0]: 'date_time'}, inplace=False)
    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df[['date_time', 'T', 'U', 'Ff', 'ff10', 'ff3', 'Tn', 'Tx', 'RRR']]
    rename_dict = {
        'T': 'temp',
        'U': 'hum',
        'Ff': 'windspeed_avg',
        'ff10': 'windspeed_max',
        'ff3': 'windspeed_max_period',
        'Tn': 'temp_min',
        'Tx': 'temp_max',
        'RRR': 'precip'
    }
    df = df.rename(columns=rename_dict, inplace=False)
    print(df)
    return df

# Example usage:
input_file = r'C:\Users\jakob\Downloads\10384.01.02.2024.10.02.2024.1.0.0.en.utf8.00000000.csv\10384.01.02.2024.10.02.2024.1.0.0.en.utf8.00000000.csv'
output_file = r'C:\Users\jakob\Downloads\10384.01.02.2024.10.02.2024.1.0.0.en.utf8.00000000.csv\10384.01.02.2024.10.02.2024.1.0.0.en.utf8.00000000_v2.csv'
filter_csv(input_file, output_file)
df = format_dataframe(output_file)
