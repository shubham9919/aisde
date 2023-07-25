from common.database.database_connection import MongoDatabase
from datetime import date, timedelta


today = date.today()
db = MongoDatabase().get_db()

BSS_Scores = db.BSSOutput
BSS_Dump = db.BSSDump
NVD_db = db.NVD_Database
CyberSix_db = db.Cybersix_Data
domain_api_db = db.domain_api_db
predicted_scores_db = db.predicted_scores_db
predicted_website_db = db.predicted_website_db
website_db = db.website_db
CVE_db = db.CVE_trend_db
BSS_trend = db.BSS_trend_db
Comapny_db = db.Company_db
Trend_Results_db = db.Trend_results_db
Results_db = db.Results_db


""" def get_latest_TEV_data_from_db(current_db, company):
    try:
        data = (
            current_db.find({"company_name": company})
            .sort("timestamp", pymongo.DESCENDING)
            .limit(1)
        )
    except Exception as err:
        print("Error", err)
        return False
    res = list(data)
    if len(res) == 0:
        return None
    return res[0]
 """

# print(get_latest_TEV_data_from_db(predicted_scores_db, "auto parts"))
# trend_id = ["CVE-2020-0002", "CVE-2020-0654", "CVE-2020-0655", "CVE-2020-0652"]

# from common.api_utils import get_website_data_from_api, process_data


# def get_all_collections(current_db):
#     return current_db.find({})


# def get_data_from_current_db(current_db, hostname):
#     try:
#         data = current_db.find_one({"hostname": hostname})
#     except Exception as err:
#         return False
#     return data


# # data = get_all_collections(predicted_website_db).distinct("hostname")
# data = ["www.boeing.com"]

# i = 0
# for item in data:
#     req = dict()
#     doc = dict()
#     req["hostname"] = item
#     print(req["hostname"])
#     doc = get_website_data_from_api(req)

#     if doc["status"] == 200:
#         api_data = doc["output"]["data"]
#         api_data["date_executed"] = str(today)
#         insert_data_in_db(website_db, api_data)
#         response_with_features = process_data(api_data)
#         response_with_features["date_executed"] = str(today)

#         if "trustgrade" not in api_data.keys():
#             response_with_features["features"]["trustgrade"] = " "
#         else:
#             response_with_features["features"]["trustgrade"] = api_data["trustgrade"]
#         old_data = get_data_from_current_db(predicted_website_db, req["hostname"])
#         new_data = response_with_features

#     else:
#         continue
#     update_data(predicted_website_db, old_data, new_data)


""" old_data = get_data_from_current_db(predicted_website_db, "www.google.com")
new_data = {
    "features": {
        "company": "google",
        "hostname": "www.google.com",
        "loadtime": 0,
        "changes": 0,
        "cloudscore": 0,
        "domainlength": 0,
        "eii": 0,
        "forwardingcount": 0,
        "htmlsize": 0,
        "incominglinks": 0,
        "subdomainscount": 0,
        "outgoinglinks": 0,
        "pagesindexed": 0,
        "pages": 0,
        "seo": 0,
        "trustscore": 0,
        "securityscore": 0,
        "visitorsavg": 0,
        "visitors": 0,
        "grade": 0,
        "trustgrade": "A",
        "trafficindex": 0,
        "websiteage": 0,
        "ecommercequality": 0,
    },
    "success": True,
    "predictions": {"probability": 0.86, "class": 1},
    "hostname": None,
    "date_executed": "2022-08-26",
} """

# update_data(predicted_website_db, old_data, new_data)


""" def get_domain_api_data(domain, company):
    data = get_domain_api(domain)
    tech = extract_tech(data)
    tev_dict = dict()
    tev_dict["comapny"] = company
    tev_dict["technologies"] = tech
    return tev_dict
 """

""" from common.tev_utils import get_company_details_from_db, domain_api_db
from common.api_utils import get_domain_api_data

# print(tev_pipeline("nike", "www.nike.com"))
# print(get_domain_api_data("www.yahoo.com", "yahoo"))


comp = list()
host = list()
comp, host = get_comp_hostnames()

for i in range(len(comp)):
    data = domain_api_db.update_one(
        {"company": comp[i]}, {"$set": {"company": comp[i].lower()}}
    )
 """


# company = "google"
# hostname = "www.google.com"
# cbl_data = computerCBL(hostname)
# bss_data = computeBSS(company)
# tev_data = computeTEV(company, hostname)
# print(get_data_from_current_db(website_db, hostname))
# print(cbl_data)
# print(bss_data)
# print(tev_data)


# print(computeBSS("meta"))

# print(computerCBL("www.boeing.com"))
# print(computerCBL("www.google.com"))
# print(computerCBL("www.youtube.com"))
# print(computerCBL("www.twitch.tv"))

# print(BSS_pipeline("samsung"))
# Imports the Google Cloud client library

# print(len(BSS_trend.distinct("Company")))


# tev_trend_pipeline_all_companies()
# ara()


# i = 0
# for item in comp:
#     print(i)
#     i = i + 1
#     res = dict()
#     final_res = list()
#     data = bssdatelogger(item, "2022-08-31", "2022-09-01")
#     update_bss_daily_scores(BSS_trend1, data["BSS"], data["Company"], data["To_Date"])
#     print(data["BSS"])
# insert_data_many(BSS_trend1, final_res)


# # for TEV
# def TEVDataCollector():
#     all_comp = domain_api_db.distinct("company")
#     i = 0
#     for item in all_comp:
#         print(i)
#         i = i + 1
#         data = tev_pipeline(item)
#         update_tev_daily_scores(
#             CVE_db,
#             data["nvd_score"],
#             data["css_score"],
#             data["company_name"],
#             data["Date"],
#         )
#         predicted_scores_db.insert_one(data)


# # for BSS
# def BSSDataCollector():
#     comp = BSS_trend1.distinct("Company")
#     i = 0
#     for item in comp:
#         i = i + 1
#         print(i)
#         data = bssdatelogger(item, str(yesterday), str(today))
#         update_bss_daily_scores(
#             BSS_trend1, data["BSS"], data["Company"], data["To_Date"]
#         )
#         BSS_trend1.insert_one(data)


# # for CBL
# def CBLDataCollector():
#     for item in hostListData:
#         old_data = website_db.find_one({"$or": [{"hostname": item}, {"domain": item}]})
#         response = get_website_data_from_api(item)
#         if response["status"] == 200:
#             api_data = response["output"]["data"]
#             api_data["date_executed"] = str(today)
#             insert_data_in_db(website_db, api_data)
#             response_with_features = process_data(api_data)
#             response_with_features["date_executed"] = str(today)
#             if "trustgrade" not in api_data.keys():
#                 response_with_features["features"]["trustgrade"] = " "
#             else:
#                 response_with_features["features"]["trustgrade"] = api_data[
#                     "trustgrade"
#                 ]
#             if old_data is None:
#                 insert_data_in_db(predicted_website_db, response_with_features)
#             else:
#                 new_data = response_with_features
#                 update_data(predicted_website_db, old_data, new_data)

# company = "trustap"
# BSS_trend.update_one({"Company": company}, {"$pop": {"BSS": 1}})
# BSS_trend.update_one({"Company": company}, {"$push": {"BSS": 0}})


# def get_latest_TEV_data_from_db(current_db, company):

#     data = (
#         current_db.find({"company_name": company})
#         .sort("Date", pymongo.DESCENDING)
#         .limit(1)
#     )
#     res = list(data)
#     if len(res) == 0:
#         return None
#     return res[0]


import datetime

today = datetime.date.today()
yesterday = today - timedelta(1)
# print(get_latest_TEV_data_from_db(predicted_scores_db, "google"))
# print(str(today))


# from common.BSS_utils import BSS_pipeline, bssdatelogger

# print(bssdatelogger("google", str(yesterday), str(today)))


# data = BSS_trend.find_one({"Company": "trustap"})
# print(data["Date"][-1])

# data = BSS_trend.distinct("Company")
# data2 = CVE_db.distinct("company_name")
# Data = set(data + data2)

# for item in data:
#     print(item)




# df = pd.read_excel("company-hostname list.xlsx")
# print(df.head())

# df = df.iloc[2:, 1:3]
# companies = df.iloc[:, 0].to_list()
# hostnames = df.iloc[:, 1].to_list()
# # print(hostnames)
# # companies = [item.lower() for item in companies]
# for i in range(len(hostnames)):
#     res = dict()
#     hostnames[i] = hostnames[i].replace("https://", "")
#     hostnames[i] = hostnames[i].replace("http://", "")
#     hostnames[i] = hostnames[i].split("/")[0]
# res["ID"] = i
# res["Company"] = companies[i]
# res["Hostname"] = hostnames[i]
# Comapny_db.insert_one(res)

# ID_list = Comapny_db.distinct("ID")
# i = 0
# for item in ID_list:
#     print(i)
#     data = Comapny_db.find_one({"ID": item})
#     if (
#         data["Company"] == "meta"
#         or data["Company"] == "microsoft"
#         or data["Company"] == "samsung"
#     ):
#         i = i + 1
#         print(data["Company"])
#         continue
#     bss_trend_data = BSS_trend.find_one({"Company": data["Company"]})
#     cve_trend_data = CVE_db.find_one({"company_name": data["Company"]})
#     # print(bss_trend_data)
#     cbl_trend_data = predicted_website_db.find_one({"hostname": data["Hostname"]})
#     overall_score = computeOverallscore(
#         bss_trend_data["BSS"][-1],
#         cve_trend_data["nvd_score"][-1],
#         cve_trend_data["css_score"][-1],
#         cbl_trend_data["predictions"]["probability"] * 10,
#         data["Company"],
#     )
#     overall_trend_data = Overall_trend.find_one({"Company": data["Company"]})
#     res = dict()
#     res["ID"] = i
#     res["nvd_score"] = cve_trend_data["nvd_score"]
#     res["nvd_Date"] = cve_trend_data["Date"]
#     res["css_score"] = cve_trend_data["css_score"]
#     res["css_Date"] = cve_trend_data["Date"]
#     res["overall_score"] = overall_trend_data["Overall_Score"]
#     res["overall_Date"] = overall_trend_data["Date"]
#     res["breach_risk_score"] = overall_trend_data["Breach_Risk_Score"]
#     res["breach_Date"] = overall_trend_data["Date"]
#     res["bss_score"] = bss_trend_data["BSS"]
#     res["bss_date"] = bss_trend_data["Date"]

#     Trend_Results_db.insert_one(res)
#     i = i + 1


# ID_list = Comapny_db.distinct("ID")
# i = 0
# for item in ID_list:
#     print(i)
#     res = dict()
#     data = Comapny_db.find_one({"ID": item})
#     if (
#         data["Company"] == "meta"
#         or data["Company"] == "microsoft"
#         or data["Company"] == "samsung"
#     ):
#         i = i + 1
#         print(data["Company"])
#         continue
#     trend_data = Trend_Results_db.find_one({"ID": data["ID"]})
#     # TEV

#     if trend_data["css_Date"][-1] != str(today):
#         cve_data = tev_pipeline(data["Company"])
#         update_tev_trend_results_daily_scores(
#             Trend_Results_db,
#             data["ID"],
#             cve_data["nvd_score"],
#             cve_data["css_score"],
#             cve_data["Date"],
#         )
#     # BSS

#     if trend_data["bss_date"][-1] != str(today):
#         bss_data = bssdatelogger(data["Company"], str(yesterday), str(today))
#         update_bss_trend_results_daily_scores(
#             Trend_Results_db, data["ID"], bss_data["BSS"], bss_data["To_Date"]
#         )
#     # CBL

#     if trend_data["breach_Date"][-1] != str(today):
#         cbl_data = computerCBL(data["Hostname"])
#         update_cbl_trend_results_daily_scores(
#             Trend_Results_db,
#             data["ID"],
#             cbl_data["predictions"]["probability"] * 10,
#             cbl_data["date_executed"],
#         )
#     # overall

#     if trend_data["overall_Date"][-1] != str(today):
#         overall_score = computeOverallscore(
#             bss_data["BSS"],
#             cve_data["nvd_score"],
#             cve_data["css_score"],
#             cbl_data["predictions"]["probability"] * 10,
#             data["Company"],
#         )
#         update_overall_trend_results_daily_scores(
#             Trend_Results_db, data["ID"], overall_score, str(today)
#         )
#     trend_data = Trend_Results_db.find_one({"ID": data["ID"]})
#     res["ID"] = i
#     res["nvd_score"] = trend_data["nvd_score"][-1]
#     res["css_score"] = trend_data["css_score"][-1]
#     res["nvd_Date"] = trend_data["nvd_Date"][-1]
#     res["css_Date"] = trend_data["css_Date"][-1]
#     res["overall_score"] = trend_data["overall_score"][-1]
#     res["overall_Date"] = trend_data["overall_Date"][-1]
#     res["breach_risk_score"] = trend_data["breach_risk_score"][-1]
#     res["breach_Date"] = trend_data["breach_Date"][-1]
#     res["bss_score"] = trend_data["bss_score"][-1]
#     res["bss_Date"] = trend_data["bss_date"][-1]
#     Results_db.insert_one(res)
#     i = i + 1

# get top CVE data

# import json

# f = open(
#     "C:\\Users\\VisionBox\\Visionary_Farm\\GDELT\\BSS\\Overall_package\\datasets\\Extracted_NVD_Data.json",
#     encoding="utf8",
# )

# # returns JSON object as a dictionary
# data = json.load(f)
# result = list()
# for item in data.keys():
#     res = dict()
#     res["CVE"] = item
#     res["technologies"] = data[item][0]
#     res["scores"] = data[item][1]
#     res["link"] = data[item][2]["link"]
#     result.append(res)
# NVD_db.insert_many(result)
##############snippet to change overall values#######################################
# ids = Results_db.distinct("ID")
# for item in ids:
#     data = Results_db.find_one({"ID": item})
#     comp = Comapny_db.find_one({"ID": item})
#     data["nvd_score"] = squish(
#         data["nvd_score"], old_nvd_min, old_nvd_max, new_nvd_min, new_nvd_max
#     )
#     data["css_score"] = squish(
#         data["css_score"], old_css_min, old_css_max, new_css_min, new_css_max
#     )
#     data["bss_score"] = squish(data["bss_score"])
#     overall_score = computeOverallscore(
#         data["bss_score"],
#         data["nvd_score"],
#         data["css_score"],
#         data["breach_risk_score"],
#         comp["Company"],
#     )
#     Trend_Results_db.update_one({"ID": item}, {"$pop": {"overall_score": 1}})
#     Trend_Results_db.update_one(
#         {"ID": item}, {"$push": {"overall_score": overall_score}}
#     )


# Trend_Results_db.update_one({"ID": 55}, {"$push": {"breach_risk_score": 9.9}})
# Trend_Results_db.update_one({"ID": 55}, {"$push": {"breach_Date": str(today)}})


# import os

# def update_css_db():
#     if len(os.listdir(CSS_PATH)) == 1:  # if we have new file
#         file = os.listdir(CSS_PATH)[0]
#     file_path = os.path.join(CSS_PATH, file)
#     f = open(file_path, encoding="utf8")
#     data = json.load(f)
#     external_ids = []
#     scores = []
#     empty = {}
#     temp = list()
#     res = dict()
#     for obj in data["objects"]:
#         if "external_references" in obj:
#             external_ids.append(obj["external_references"][0]["external_id"])
#         if "x_sixgill_info" in obj:
#             if not obj["x_sixgill_info"]["score"]:
#                 scores.append(empty)
#             scores.append(obj["x_sixgill_info"]["score"])

#     for i in range(len(external_ids)):
#         res = dict()
#         data = bundle_api_db.find_one({"external_id": external_ids[i]})
#         if not data:
#             res["external_id"] = external_ids[i]
#             res["x_sixgill_score"] = scores[i]
#             print(external_ids[i])
#             temp.append(res)
#         else:
#             bundle_api_db.update_one(
#                 {"external_id": external_ids[i]},
#                 {"$set": {"x_sixgill_score": scores[i]}},
#             )
#     if len(temp) != 0:
#         bundle_api_db.insert_many(temp)

#     os.remove(file_path)


# update_css_db()
# print(bundle_api_db.find_one({"external_id": "CVE-2022-34526"}))
# path = "datasets\\ExternalIDs1.json"
# f = open(path, encoding="utf8")
# data = json.load(f)
# print(len(data))

# for item in data:
#     temp = dict()
#     data = bundle_api_db.find_one({"external_id": item["external_id"]})
#     if not data:
#         temp["external_id"] = item["external_id"]
#         temp["x_sixgill_score"] = item["x_sixgill_score"]
#         bundle_api_db.insert_one(temp)
#     else:
#         continue

# print(bundle_api_db.index_information())


# res = dict()
# result = list()
# ids = Company_db.distinct("ID")
# for item in ids:
#     if item == 77 or item == 95 or item == 78:
#         continue
#     comp_data = Company_db.find_one({"ID": item})
#     tev_data = tev_pipeline(comp_data["Company"])
#     res["ID"] = item
#     res["Company"] = comp_data["Company"]
#     res["NVD"] = tev_data["nvd_score"]
#     res["CSS"] = tev_data["css_score"]
#     result.append(res)
#     print(res)


# tech = ["google", "apache", "wordpress", "asp.net", "microsoft"]
# # css_id = bundle_api_db.distinct("external_id")
# nvd_id = list(NVD_db.find({"technologies.0": {"$exists": True}}))
# # res = list(set(nvd_id).intersection(css_id))
# print(len(nvd_id))


# ids_at_risk = []
# scores = []
# links = []


# nvd_data = list(NVD_db.find({"technologies.0": {"$exists": True}}))
# for item in nvd_data:
#     if len(list(set(item["technologies"]).intersection(tech))) > 0:
#         ids_at_risk.append(item["CVE"])
#         scores.append(item["scores"])
#         links.append(item["link"])

# print(len(ids_at_risk))
# print(len(scores))
# print(len(links))
# bss_data = bssdatelogger("tesla", str(yesterday), str(today))


# ids = vendor_risk_db.distinct("ID")
# for item in ids:
#     res = dict()
#     comp = Comapny_db.find_one({"ID": item})
#     if (
#         comp["Company"] == "meta"
#         or comp["Company"] == "samsung"
#         or comp["Company"] == "microsoft"
#     ):
#         continue
#     res_data = Results_db.find_one({"ID": item})
#     res["ID"] = item
#     res["Company"] = comp["Company"]
#     web_data = website_db.find_one(
#         {"$or": [{"hostname": comp["Hostname"]}, {"domain": comp["Hostname"]}]}
#     )
#     if web_data is None:
#         continue
#     if web_data["domain"] is None:
#         res["Domain"] = "Unknown"
#     res["Domain"] = web_data["domain"]
#     if "sicdivision" not in web_data.keys():
#         res["Industry"] = "Unknown"
#     else:
#         res["Industry"] = web_data["sicdivision"]
#     if res_data["overall_score"] > 6.0 and res_data["overall_score"] <= 9.0:
#         res["Status"] = "High"
#     elif res_data["overall_score"] > 3.0 and res_data["overall_score"] <= 6.0:
#         res["Status"] = "Medium"
#     elif res_data["overall_score"] > 0.0 and res_data["overall_score"] <= 3.0:
#         res["Status"] = "Low"
#     else:
#         res["Status"] = "Critical"
#     print(res["Status"])
#     res_data["nvd_score"] = squish(
#         res_data["nvd_score"], old_nvd_min, old_nvd_max, new_nvd_min, new_nvd_max
#     )
#     res_data["css_score"] = squish(
#         res_data["css_score"], old_css_min, old_css_max, new_css_min, new_css_max
#     )
#     res_data["bss_score"] = squish(res_data["bss_score"])

#     res["Alert_Type"] = findMaxScore(
#         res_data["breach_risk_score"],
#         res_data["nvd_score"],
#         res_data["css_score"],
#         res_data["bss_score"],
#     )
#     res["Date"] = str(today)

#     vendor_risk_db.update_one({"ID": item}, {"$set": {"Status": res["Status"]}})
#     vendor_risk_db.update_one({"ID": item}, {"$set": {"Alert_Type": res["Alert_Type"]}})
# checkpoint = today - timedelta(4)
# print(checkpoint)


# nvd_ids = NVD_db.distinct("CVE")
# print(len(nvd_ids))

# ids = get_all_collections(bundle_api_db).distinct("external_id")
# css_ids = bundle_api_db.distinct("external_id")
# res = list(set(nvd_ids).intersection(css_ids))
# print(len(res))

# nvd_data = list(NVD_db.find({"technologies.0": {"$exists": True}}))
# print(len(nvd_data))
# tech_at_risk = ["asp.net", "apache"]
# ids_at_risk = []
# scores = []
# links = []
# # all documents with at least 1 element in technologies
# f = open(EXTRACTED_NVD_DATA_LOCATION, encoding="utf8")
# data = json.load(f)
# for item in data.keys():
#     if not data[item][0]:
#         continue
#     else:
#         for i in tech_at_risk:
#             if i in data[item][0]:
#                 ids_at_risk.append(item)
#                 scores.append(data[item][1])
#                 links.append(data[item][2])
# print(ids_at_risk)


# for item in ids_at_risk:
#     data = bundle_api_db.find_one({"external_id": item})
#     if not data:
#         continue
#     common_ids.append(item)
#     external_score.append(data["x_sixgill_score"])


# without DB
# f = open(EXTERNAL_IDS_LOCATION, encoding="utf8")
# data = json.load(f)
# for item in ids_at_risk:
#     if item in data.keys():
#         common_ids.append(item)
#         external_score.append(data[item])

# print(common_ids)
# print(len(external_score))
# arr = ["CVE-2020-35452", "CVE-2020-13950", "CVE-2020-1181"]
# for item in arr:
#     print(NVD_db.find_one({"CVE": item}))

# print(tev_pipeline("abbott"))
# create_new_comp_data("uber", "www.uber.com")

# start = 15
# trend_data = Trend_Results_db.find_one({"ID": 128})
# for i in range(16):
#     checkpoint2 = today - timedelta(start)
#     trend_data["css_score"][i] = squish(
#         trend_data["css_score"][i],
#         old_css_min,
#         old_css_max,
#         new_css_min,
#         new_css_max,
#     )
#     trend_data["nvd_score"][i] = squish(
#         trend_data["nvd_score"][i],
#         old_nvd_min,
#         old_nvd_max,
#         new_nvd_min,
#         new_nvd_max,
#     )
#     trend_data["bss_score"][i] = squish(trend_data["bss_score"][i])
#     overall_score = computeOverallscore(
#         trend_data["bss_score"][i],
#         trend_data["nvd_score"][i],
#         trend_data["css_score"][i],
#         trend_data["breach_risk_score"][i],
#     )
#     update_overall_trend_results_daily_scores(
#         Trend_Results_db, 128, overall_score, str(checkpoint2)
#     )
#     # updating results db
#     Results_db.update_one({"ID": 128}, {"$set": {"overall_score": overall_score}})
#     Results_db.update_one({"ID": 128}, {"$set": {"overall_Date": str(checkpoint2)}})
#     start = start - 1
# import time

# start_time = time.time()
# new_comp_data_prep("unity", "www.unity.com")
# print("--- %s seconds ---" % (time.time() - start_time))
# print(Results_db.find_one({"ID": 129}))
# print(str(DByesterday))
# i = 0
# id_list = Company_db.distinct("ID")
# print(id_list)
# for item in range(128):
#     print(i)
#     if item == 77 or item == 78 or item == 95:
#         i = i + 1
#         continue
#     trend_data = Trend_Results_db.find_one({"ID": item})
#     Trend_Results_db.update_one({"ID": item}, {"$pop": {"bss_date": 1}})
#     Trend_Results_db.update_one({"ID": item}, {"$push": {"bss_date": str(DByesterday)}})

#     i = i + 1


# print(max_score_list)


# we are going to find out the change in BSS scores for today and yesterdat, check its %change and assign a score.
# id = Trend_Results_db.distinct("ID")
# temp = list()
# for item in id:
#     trend_data = Trend_Results_db.find_one({"ID": item})
#     initial_bss = trend_data["bss_score"][-2]
#     final_bss = trend_data["bss_score"][-1]
#     if initial_bss == 0:
#         print("item:", item)
#         change = round(((final_bss - initial_bss) / 1) * 100, 2)
#     else:
#         print("item:", item)
#         change = round(((final_bss - initial_bss) / initial_bss) * 100, 2)
#     if change >= 0 and change < 100:
#         new_change = ((change - 0) / (100 - 0)) * (2.5 - 0) + 0.0
#     elif change >= -100 and change < 0:
#         new_change = ((change + 100) / (100)) * (2.5 - 0) + 0.0
#     elif change >= 100 and change < 300:
#         new_change = ((change - 100) / (300 - 100)) * (5.0 - 2.5) + 2.5
#     elif change >= -300 and change < -100:
#         new_change = ((change + 300) / (-100 + 300)) * (5.0 - 2.5) + 2.5
#     elif change >= 300 and change < 600:
#         new_change = ((change - 300) / (600 - 300)) * (7.5 - 5.0) + 5.0
#     elif change >= -600 and change < -300:
#         new_change = ((change + 600) / (-300 + 600)) * (7.5 - 5.0) + 5.0
#     elif change >= 600 and change < 1000:
#         new_change = ((change - 600) / (1000 - 600)) * (10 - 7.5) + 7.5
#     elif change >= -1000 and change < -600:
#         new_change = ((change + 1000) / (-600 + 1000)) * (10 - 7.5) + 7.5
#     elif change <= -1000 or change >= 1000:
#         new_change = 10.0
#     new_change = round(new_change, 2)
#     print(new_change)
#     temp.append(new_change)

# print(temp)


def compute_brandSentimentScore(ID):
    trend_data = Trend_Results_db.find_one({"ID": ID})
    initial_bss = trend_data["bss_score"][-2]
    final_bss = trend_data["bss_score"][-1]
    if final_bss - initial_bss < 0:
        sign = -1
    else:
        sign = 1
    if initial_bss == 0:
        change = round(((final_bss - initial_bss) / 1) * 100 * sign, 2)
    else:
        change = round(((final_bss - initial_bss) / abs(initial_bss)) * 100 * sign, 2)
    if change >= 0 and change < 100:
        new_change = ((change - 0) / (100 - 0)) * (2.5 - 0) + 0.0
    elif change >= -100 and change < 0:
        new_change = ((change + 100) / (100)) * (2.5 - 0) + 0.0
    elif change >= 100 and change < 300:
        new_change = ((change - 100) / (300 - 100)) * (5.0 - 2.5) + 2.5
    elif change >= -300 and change < -100:
        new_change = ((change + 300) / (-100 + 300)) * (5.0 - 2.5) + 2.5
    elif change >= 300 and change < 600:
        new_change = ((change - 300) / (600 - 300)) * (7.5 - 5.0) + 5.0
    elif change >= -600 and change < -300:
        new_change = ((change + 600) / (-300 + 600)) * (7.5 - 5.0) + 5.0
    elif change >= 600 and change < 1000:
        new_change = ((change - 600) / (1000 - 600)) * (10 - 7.5) + 7.5
    elif change >= -1000 and change < -600:
        new_change = ((change + 1000) / (-600 + 1000)) * (10 - 7.5) + 7.5
    elif change <= -1000 or change >= 1000:
        new_change = 10.0
    new_change = round(new_change, 2)
    return new_change


# for i in reversed(range(21)):

# ids = Trend_Results_db.distinct("ID")

# for item in ids:
#     trend_data = Trend_Results_db.find_one({"ID": item})
#     list_len = len(trend_data["bss_score"])
#     bss_score_list = list()
#     for i in reversed(range(list_len + 1)):
#         initial_bss = trend_data["bss_score"][-i]
#         final_bss = trend_data["bss_score"][-i + 1]
#         if final_bss - initial_bss < 0:
#             sign = -1
#         else:
#             sign = 1
#         if initial_bss == 0:
#             change = round(((final_bss - initial_bss) / 1) * 100 * sign, 2)
#         else:
#             change = round(
#                 ((final_bss - initial_bss) / abs(initial_bss)) * 100 * sign, 2
#             )
#         if change >= 0 and change < 100:
#             new_change = ((change - 0) / (100 - 0)) * (2.5 - 0) + 0.0
#         elif change >= -100 and change < 0:
#             new_change = ((change + 100) / (100)) * (2.5 - 0) + 0.0
#         elif change >= 100 and change < 300:
#             new_change = ((change - 100) / (300 - 100)) * (5.0 - 2.5) + 2.5
#         elif change >= -300 and change < -100:
#             new_change = ((change + 300) / (-100 + 300)) * (5.0 - 2.5) + 2.5
#         elif change >= 300 and change < 600:
#             new_change = ((change - 300) / (600 - 300)) * (7.5 - 5.0) + 5.0
#         elif change >= -600 and change < -300:
#             new_change = ((change + 600) / (-300 + 600)) * (7.5 - 5.0) + 5.0
#         elif change >= 600 and change < 1000:
#             new_change = ((change - 600) / (1000 - 600)) * (10 - 7.5) + 7.5
#         elif change >= -1000 and change < -600:
#             new_change = ((change + 1000) / (-600 + 1000)) * (10 - 7.5) + 7.5
#         elif change <= -1000 or change >= 1000:
#             new_change = 10.0
#         new_change = round(new_change, 2)
#         bss_score_list.append(new_change)
#     Trend_Results_db.update_one({"ID": item}, {"$set": {"BSS": bss_score_list}})


# print(len(Trend_Results_db.find_one({"ID": 129})["bss_score"]))

# for item in ids:
#     trend_data = Trend_Results_db.find_one({"ID": item})
#     overall = computeOverallscore(
#         trend_data["BSS"][-1],
#         trend_data["nvd_score"][-1],
#         trend_data["css_score"][-1],
#         trend_data["breach_risk_score"][-1],
#     )
#     Trend_Results_db.update_one({"ID": item}, {"$pop": {"overall_score": 1}})
#     Trend_Results_db.update_one({"ID": item}, {"$push": {"overall_score": overall}})

# all_comp = list(Results_db.find({}))
# max_score_list = sorted(all_comp, key=lambda d: d["overall_score"])
# print(max_score_list)


today = date.today()
yesterday = today - timedelta(64)
print(yesterday)
# from common.BOR_utils import BOR

# BOR("www.avalere.com")
# from common.tev_utils import tev_logger
# print(tev_logger("nike", today ))
# print(bssdatelogger("rockstar", "2022-09-1", "2022-09-19"))
# bss_score = list()
# start_date = today - timedelta(48)
# print(start_date)
# for i in range(0, 11):
#     from_date = start_date + timedelta(i)
#     to_date = start_date + timedelta(i + 1)
#     bss_score.append(bssdatelogger("microsoft", from_date, to_date)["BSS"])

# print(bss_score)
    # check for new files in the path, if yes add then check and to bundle api
    #update_css_db()