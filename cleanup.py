import pandas as pd

def delete_comments_from_csv(input_file, output_file):

    with open(input_file, 'r', newline='') as infile:
        csv_content = infile.read()

    rows = csv_content.split('\n')
    non_comment_index = next((i for i, row in enumerate(rows) if not row.startswith('#')), len(rows))
    new_csv_content = '\n'.join(rows[non_comment_index:])

    with open(output_file, 'w', newline='') as outfile:
        outfile.write(new_csv_content)

def format_dataframe(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=';', decimal='.', index_col=False)
    df = df.rename(columns={df.columns[0]: 'date_time'}, inplace=False)
    df['date_time'] = pd.to_datetime(df['date_time'])
    relevant_columns = ['date_time', 'T', 'U', 'Ff', 'ff10', 'ff3', 'Tn', 'Tx', 'RRR']
    df = df[[col for col in df.columns if col in relevant_columns]]
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
    return df
