# imports
import os
from datetime import date, timedelta
from common.utils_external import gcp2df
from common.config_constants import KEY_PATH
from common.constant_variables import QUERY

# setting envoirment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# saving user inputs
today = date.today()
yesterday = today - timedelta(days=1)

# a function to find sentiment score for a company today
def find_daily_bss(company):
    result1 = dict()
    company = company.lower()
    todate = f'\n  AND DATE(_PARTITIONTIME) < "{str(today)}"'
    organizations = f"\n  AND lower(V2Organizations) LIKE  '%{company} %'"
    fromdate = f'  DATE(_PARTITIONTIME) >= "{str(yesterday)}"'
    query = QUERY + fromdate + todate + organizations

    # ask the big query client to fetch the results for our query and convert them into a Data Frame
    df = gcp2df(query)

    # If we do not find any documents for the comapny, exit
    if df.shape[0] == 0:
        print(f"\n No new documents found today for {company}!")
        result1["Company"] = company
        result1["BSS"] = 0
        result1["Total_Tone_value"] = 0
        result1["Total_documents_Collected"] = 0
        result1["From_Date"] = str(yesterday)
        result1["To_Date"] = str(today)
        return result1

    sum_tone = df["tone"].sum()

    # BSS computation
    BSS = round((sum_tone / df.shape[0]), 4)

    # storing results in a Db
    result1["Company"] = company
    result1["BSS"] = BSS
    result1["Total_Tone_value"] = round(sum_tone, 3)
    result1["Total_documents_Collected"] = df.shape[0]
    result1["From_Date"] = str(yesterday)
    result1["To_Date"] = str(today)
    return result1

# a function to find sentiment score for a company for any given day/ date range
def bssdatelogger(company, fromd, tdate):
    result = dict()
    company = company.lower()
    todate = f'\n  AND DATE(_PARTITIONTIME) < "{str(tdate)}"'
    organizations = f"\n  AND lower(V2Organizations) LIKE  '%{company} %'"
    fromdate = f'  DATE(_PARTITIONTIME) >= "{str(fromd)}"'
    query = QUERY + fromdate + todate + organizations

    # ask the big query client to fetch the results for our query and convert them into a Data Frame
    df = gcp2df(query)

    # If we do not find any documents for the comapny, exit
    if df.shape[0] == 0:
        print(f"\n No new documents found today for {company}!")
        result["Company"] = company
        result["BSS"] = 0
        result["Total_Tone_value"] = 0
        result["Total_documents_Collected"] = 0
        result["From_Date"] = str(fromd)
        result["To_Date"] = str(tdate)
        return result

    sum_tone = df["tone"].sum()

    # BSS computation
    BSS = round((sum_tone / df.shape[0]), 4)

    # storing results in a Db
    result["Company"] = company
    result["BSS"] = BSS
    result["Total_Tone_value"] = round(sum_tone, 3)
    result["Total_documents_Collected"] = df.shape[0]
    result["From_Date"] = str(fromd)
    result["To_Date"] = str(tdate)
    return result
