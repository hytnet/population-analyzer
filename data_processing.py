import pandas as pd

def get_population_data(filename, year, population_type='total'):
    sheet_map = {
        'total': 0,
        'under_15': 1,
        'age_15_64': 2,
        'over_65': 3,
        'male_total': 4,
        'male_under_15': 5,
        'male_15_64': 6,
        'male_over_65': 7,
        'female_total': 8,
        'female_under_15': 9,
        'female_15_64': 10,
        'female_over_65': 11
    }
    sheet_index = sheet_map[population_type]
    df = pd.read_excel(filename, sheet_name=sheet_index, skiprows=10)
    print(df.columns.tolist())
    df.columns = [str(col).strip() for col in df.columns]
    year_col = str(year)
    df = df[['GEO (Codes)', 'GEO (Labels)', year_col]]
    df = df.rename(columns={'GEO (Codes)': 'NUTS_ID', 'GEO (Labels)': 'NUTS_NAME', year_col:'Population'})
    df = df.dropna(subset=['NUTS_ID'])
    df['NUTS_ID'] = df['NUTS_ID'].astype(str).str.strip()
    return df