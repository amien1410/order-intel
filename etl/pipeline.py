from etl.extract import extract_csv
from etl.transform import transform_data
from etl.load import load_to_mongo

if __name__ == "__main__":
    df = extract_csv("data/raw/sample_data.csv")
    records = transform_data(df)
    load_to_mongo(records, "transactions")
