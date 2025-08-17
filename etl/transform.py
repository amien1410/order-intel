def transform_data(df):
    print("Transforming data...")
    df = df.dropna()
    df.columns = [col.lower() for col in df.columns]
    return df.to_dict(orient="records")
