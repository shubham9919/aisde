import collections
from common.database.database_connection import MongoDatabase
import os
import json
from common.config_constants import CSS_PATH

db = MongoDatabase().get_db()

# getting collections
predicted_website_db = db.predicted_website_db
website_db = db.website_db
batch_db = db.batch_db
domain_api_db = db.domain_api_db
bundle_api_db = db.bundle_api_db
predicted_scores_db = db.predicted_scores_db
NVD_db = db.NVD_Database
CVE_db = db.CVE_trend_db
Company_db = db.Company_db
Results_db = db.Results_db
Trend_Results_db = db.Trend_results_db
top_cve_db = db.Top_cve_data
vendor_risk_db = db.Vendor_risk_db

# function to insert a new document
def insert_data(current_db, new_data):
    try:
        current_db.insert_one(new_data)
    except Exception as err:
        print("Error", err)
        return False

    return True


# A function to insert data into any given db
def insert_data_in_db(current_db, new_data):
    old_data = get_data_from_current_db(current_db, new_data["hostname"])
    new_data = collections.OrderedDict(sorted(new_data.items()))

    if old_data:
        return update_data(current_db, old_data, new_data)
    else:
        return insert_data(current_db, new_data)


# A function to get data from website/ predicted website db
def get_data_from_current_db(current_db, hostname):
    try:
        data = current_db.find_one({"hostname": hostname})
    except Exception as err:
        return False
    return data


# function to update an exixting document
def update_data(current_db, old_data, new_data):
    try:
        current_db.update_one(old_data, {"$set": new_data})
    except Exception as err:
        print("Error", err)
        return False

    return True


# function to insert many new documents at a time
def insert_data_many(current_db, new_data):
    try:
        current_db.insert_many(new_data)
    except Exception as err:
        print("Error", err)
        return False

    return True


# function to collect all documents
def get_all_collections(current_db):
    return current_db.find({})


# function to update BSS trend scores
def update_bss_daily_scores(current_db, score, company, date):
    filter = {"Company": company}
    newvalue = {"$push": {"BSS": score}}
    newvalue1 = {"$push": {"Date": date}}
    current_db.update_one(filter, newvalue)
    current_db.update_one(filter, newvalue1)


# function to update TEV trend scores
def update_tev_daily_scores(current_db, nvd, css, company, Da):
    filter = {"company_name": company}
    newvalue = {"$push": {"nvd_score": nvd}}
    newvalue1 = {"$push": {"css_score": css}}
    newvalue2 = {"$push": {"Date": Da}}
    current_db.update_one(filter, newvalue)
    current_db.update_one(filter, newvalue1)
    current_db.update_one(filter, newvalue2)


# function to update TEV scores in Trend_resukts_db
def update_tev_trend_results_daily_scores(current_db, ID, nvd, css, Da):
    filter = {"ID": ID}
    newvalue1 = {"$push": {"nvd_score": nvd}}
    newvalue2 = {"$push": {"css_score": css}}
    newvalue3 = {"$push": {"nvd_Date": Da}}
    newvalue4 = {"$push": {"css_Date": Da}}
    current_db.update_one(filter, newvalue1)
    current_db.update_one(filter, newvalue2)
    current_db.update_one(filter, newvalue3)
    current_db.update_one(filter, newvalue4)


# function to update BSS scores in Trend_results_db
def update_bss_trend_results_daily_scores(current_db, ID, bss, date, brand):
    filter = {"ID": ID}
    newvalue1 = {"$push": {"bss_score": bss}}
    newvalue2 = {"$push": {"bss_date": date}}
    newvalue3 = {"$push": {"BSS": brand}}
    current_db.update_one(filter, newvalue1)
    current_db.update_one(filter, newvalue2)
    current_db.update_one(filter, newvalue3)


# function to update CBL scores in Trend_results_db
def update_cbl_trend_results_daily_scores(current_db, ID, cbl, Da):
    filter = {"ID": ID}
    newvalue1 = {"$push": {"breach_risk_score": cbl}}
    newvalue2 = {"$push": {"breach_Date": Da}}
    current_db.update_one(filter, newvalue1)
    current_db.update_one(filter, newvalue2)


# function to update Overall scores in Trend_results_db
def update_overall_trend_results_daily_scores(current_db, ID, over, Da):
    filter = {"ID": ID}
    newvalue1 = {"$push": {"overall_score": over}}
    newvalue2 = {"$push": {"overall_Date": Da}}
    current_db.update_one(filter, newvalue1)
    current_db.update_one(filter, newvalue2)


# function to update Cyber six data
def update_css_db():
    if len(os.listdir(CSS_PATH)) > 0:  # if we have new file
        file = os.listdir(CSS_PATH)[0]
    else:
        return
    file_path = os.path.join(CSS_PATH, file)
    f = open(file_path, encoding="utf8")
    data = json.load(f)
    external_ids = []
    scores = []
    empty = {}
    temp = list()
    res = dict()
    for obj in data["objects"]:
        if "external_references" in obj:
            external_ids.append(obj["external_references"][0]["external_id"])
        if "x_sixgill_info" in obj:
            if not obj["x_sixgill_info"]["score"]:
                scores.append(empty)
            scores.append(obj["x_sixgill_info"]["score"])

    for i in range(len(external_ids)):
        res = dict()
        data = bundle_api_db.find_one({"external_id": external_ids[i]})
        if not data:
            print("\nnot here")
            res["external_id"] = external_ids[i]
            res["x_sixgill_score"] = scores[i]
            print(external_ids[i])
            temp.append(res)
        else:
            print("\nhere")
            bundle_api_db.update_one(
                {"external_id": external_ids[i]},
                {"$set": {"x_sixgill_score": scores[i]}},
            )
        if len(temp) != 0:
            bundle_api_db.insert_many(temp)
