import math
from os import walk
import pandas as pd
import glob
from google.cloud import bigquery
import os
import json


def replicate_data(dfx, required_rows):
    """
    Util method to replicate data
    """
    df = dfx.copy()
    df_copy = df.copy()

    factor = math.ceil(required_rows / df.shape[0])
    df = df.append([df_copy] * factor, ignore_index=True)
    df = df[:required_rows].reset_index(drop=True)
    return df


def write_to_csv(df):
    location = "../test/"
    name = "test_generated_"
    csv_name_loc = f"{location}{name}{df.shape[0]}.csv"
    df.to_csv(csv_name_loc)
    print(f"Saved to/as {csv_name_loc} (ROWS = {df.shape[0]})")


def get_all_file_names_from_location(location):
    filenames = next(walk(location), (None, None, []))[2]
    return filenames

# function to connect to bigquery
def gcp2df(sql):

    # connecting to bigquery client
    client = bigquery.Client()
    query = client.query(sql)
    results = query.result()
    return results.to_dataframe()


# Function to find the latest date for whih the BSS was calculated
def findLatestDate(Company):

    # getting the list of all file for that company folder
    list_of_files = glob.glob(
        f".\\Output\\{Company}\\*.json"
    )  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_date = latest_file[-15:-5]
    return latest_date


def writeOP(df, company, today):
    path = f".\\Output\\{company}\\{company}_{str(today)}.csv"
    df.to_csv(path, index=False)


def writeJSON(res, company, today):
    # Save the dictionary as json file
    with open(f".\\Output\\{company}\\{company}_{str(today)}.json", "w") as fp:
        json.dump(res, fp, indent=4)


if __name__ == "__main__":
    required_rows = 1000000
    read_csv_name = "test2.csv"
    location = "../test/"
    read_csv_with_location = location + read_csv_name
    df = pd.read_csv(read_csv_with_location).dropna(how="all")
    df = replicate_data(df, required_rows)
    write_to_csv(df)

