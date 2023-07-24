from common.database.database_utils import (
    predicted_website_db,
    website_db,
    bundle_api_db,
    Company_db,
    Results_db,
    Trend_Results_db,
    NVD_db,
    top_cve_db,
    insert_data_in_db,
    update_data,
    update_tev_trend_results_daily_scores,
    update_bss_trend_results_daily_scores,
    update_cbl_trend_results_daily_scores,
    update_overall_trend_results_daily_scores,
    update_css_db,
)
from common.constant_variables import (
    old_css_min,
    old_css_max,
    new_css_min,
    new_css_max,
    old_nvd_min,
    old_nvd_max,
    new_nvd_min,
    new_nvd_max,
)
from common.BSS_utils import bssdatelogger
from common.tev_utils import tev_pipeline, tev_logger
from common.api_utils import get_website_data_from_api, process_data
from common.scoreUtils import (
    computeCBL,
    computeOverallscore,
    squish,
    vendor_updater,
    compute_brandSentimentScore,
)
from common.constant_variables import hostListData
from datetime import date, timedelta

today = date.today()
yesterday = today - timedelta(1)
DByesterday = today - timedelta(61)
DByesterday1 = today - timedelta(62)

# CBL data collection function
def CBLDataCollector():
    i = 0
    for item in hostListData:
        print(i)
        i = i + 1
        old_data = website_db.find_one({"$or": [{"hostname": item}, {"domain": item}]})
        response = get_website_data_from_api(item)
        if response["status"] == 200:
            api_data = response["output"]["data"]
            api_data["date_executed"] = str(today)
            insert_data_in_db(website_db, api_data)
            response_with_features = process_data(api_data)
            response_with_features["date_executed"] = str(today)
            if "trustgrade" not in api_data.keys():
                response_with_features["features"]["trustgrade"] = " "
            else:
                response_with_features["features"]["trustgrade"] = api_data[
                    "trustgrade"
                ]
            if old_data is None:
                insert_data_in_db(predicted_website_db, response_with_features)
            else:
                new_data = response_with_features
                update_data(predicted_website_db, old_data, new_data)
    print(f"Collected CBL data for {i} companies")


# once we have a paid version we can use this function to get the data for more companies
def CBLDataCollectorNew():
    host = predicted_website_db.distinct("hostname")
    for item in host:
        print(i)
        i = i + 1
        old_data = website_db.find_one({"$or": [{"hostname": item}, {"domain": item}]})
        response = get_website_data_from_api(item)
        if response["status"] == 200:
            api_data = response["output"]["data"]
            api_data["date_executed"] = str(today)
            insert_data_in_db(website_db, api_data)
            response_with_features = process_data(api_data)
            response_with_features["date_executed"] = str(today)
            if "trustgrade" not in api_data.keys():
                response_with_features["features"]["trustgrade"] = " "
            else:
                response_with_features["features"]["trustgrade"] = api_data[
                    "trustgrade"
                ]
            if old_data is None:
                insert_data_in_db(predicted_website_db, response_with_features)
            else:
                new_data = response_with_features
                update_data(predicted_website_db, old_data, new_data)
    print(f"Collected CBL data for {i} companies")


# current data collection function
def dailyDbUpdater():
    ID_list = Company_db.distinct("ID")
    i = 0
    for item in ID_list:
        res = dict()
        res1 = dict()
        print(i)
        data = Company_db.find_one({"ID": item})
        trend_data = Trend_Results_db.find_one({"ID": data["ID"]})
        if (
            data["Company"] == "meta"
            or data["Company"] == "microsoft"
            or data["Company"] == "samsung"
        ):
            i = i + 1
            print(data["Company"])
            continue

        # TEV
        if trend_data["css_Date"][-1] != str(today):
            cve_data = tev_pipeline(data["Company"])
            update_tev_trend_results_daily_scores(
                Trend_Results_db,
                data["ID"],
                cve_data["nvd_score"],
                cve_data["css_score"],
                cve_data["Date"],
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"nvd_score": cve_data["nvd_score"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"css_score": cve_data["css_score"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"nvd_Date": cve_data["Date"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"css_Date": cve_data["Date"]}}
            )
        else:
            res["nvd_score"] = trend_data["nvd_score"][-1]
            res["css_score"] = trend_data["css_score"][-1]
            cve_data = res

        # BSS
        if trend_data["bss_date"][-1] != str(today):
            bss_data = bssdatelogger(data["Company"], str(yesterday), str(today))
            update_bss_trend_results_daily_scores(
                Trend_Results_db, data["ID"], bss_data["BSS"], bss_data["To_Date"]
            )
            # updating results db
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"bss_score": bss_data["BSS"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"bss_Date": bss_data["To_Date"]}}
            )
        else:
            res1["BSS"] = trend_data["bss_score"][-1]
            bss_data = res1

        # CBL
        if trend_data["breach_Date"][-1] != str(today):
            cbl_data = computeCBL(data["Hostname"])
            update_cbl_trend_results_daily_scores(
                Trend_Results_db,
                data["ID"],
                cbl_data["predictions"]["probability"] * 10,
                cbl_data["date_executed"],
            )
            # updating results db
            Results_db.update_one(
                {"ID": data["ID"]},
                {
                    "$set": {
                        "breach_risk_score": cbl_data["predictions"]["probability"] * 10
                    }
                },
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"breach_Date": cbl_data["date_executed"]}}
            )
        else:
            cbl_data = predicted_website_db.find_one({"hostname": data["Hostname"]})

        # overall
        if trend_data["overall_Date"][-1] != str(today):
            cve_data["css_score"] = squish(
                cve_data["css_score"],
                old_css_min,
                old_css_max,
                new_css_min,
                new_css_max,
            )
            cve_data["nvd_score"] = squish(
                cve_data["nvd_score"],
                old_nvd_min,
                old_nvd_max,
                new_nvd_min,
                new_nvd_max,
            )
            bss_data["BSS"] = squish(bss_data["BSS"])

            overall_score = computeOverallscore(
                bss_data["BSS"],
                cve_data["nvd_score"],
                cve_data["css_score"],
                cbl_data["predictions"]["probability"] * 10,
            )
            update_overall_trend_results_daily_scores(
                Trend_Results_db, data["ID"], overall_score, str(today)
            )
            # updating results db
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"overall_score": overall_score}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"overall_Date": str(today)}}
            )
            i = i + 1
    vendor_updater()


# gets the top trending CVE's
def get_top_trending_cves():
    i = 0
    mins = 9
    ids = bundle_api_db.distinct("external_id")
    ids = NVD_db.distinct("CVE")
    for item in ids:
        res = dict()
        data = NVD_db.find_one({"CVE": item})
        if not data:
            continue
        if len(data["technologies"]) == 0 or data["technologies"] is None:
            continue
        if not data["scores"]:
            continue
        if not data["scores"]["ImpactScoreV2"]:
            continue

        impact = data["scores"]["ImpactScoreV2"]
        if impact > mins:
            res["CVE"] = data["CVE"]
            res["technologies"] = data["technologies"]
            res["Impact"] = impact
            res["link"] = data["link"]
            res["date"] = str(today)
            temp = top_cve_db.find_one({"CVE": res["CVE"]})
            if not temp:
                top_cve_db.insert_one(res)
            i = i + 1


# current data collection module(batch data collection for all companies)
def dailyDbUpdater1():
    ID_list = Company_db.distinct("ID")
    i = 0
    for item in ID_list:
        res = dict()
        res1 = dict()
        print(i)
        data = Company_db.find_one({"ID": item})
        trend_data = Trend_Results_db.find_one({"ID": data["ID"]})
        if (
            data["Company"] == "meta"
            or data["Company"] == "microsoft"
            or data["Company"] == "samsung"
        ):
            i = i + 1
            print(data["Company"])
            continue

        # TEV
        if trend_data["css_Date"][-1] != str(today):
            # update_css_db()
            cve_data = tev_logger(data["Company"], DByesterday)
            print(data["Company"])
            print(cve_data["nvd_score"])
            print(cve_data["css_score"])
            update_tev_trend_results_daily_scores(
                Trend_Results_db,
                data["ID"],
                cve_data["nvd_score"],
                cve_data["css_score"],
                cve_data["Date"],
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"nvd_score": cve_data["nvd_score"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"css_score": cve_data["css_score"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"nvd_Date": cve_data["Date"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"css_Date": cve_data["Date"]}}
            )
        else:
            res["nvd_score"] = trend_data["nvd_score"][-1]
            res["css_score"] = trend_data["css_score"][-1]
            cve_data = res

        # BSS
        if trend_data["bss_date"][-1] != str(today):
            bss_data = bssdatelogger(
                data["Company"], str(DByesterday1), str(DByesterday)
            )
            bss_data["brand"] = compute_brandSentimentScore(item, bss_data["BSS"])
            print(bss_data["BSS"])
            update_bss_trend_results_daily_scores(
                Trend_Results_db,
                data["ID"],
                bss_data["BSS"],
                bss_data["To_Date"],
                bss_data["brand"],
            )
            # updating results db
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"bss_score": bss_data["BSS"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"bss_Date": bss_data["To_Date"]}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"BSS": bss_data["brand"]}}
            )
        else:
            res1["BSS"] = trend_data["BSS"][-1]
            bss_data = res1

        # CBL
        if trend_data["breach_Date"][-1] != str(today):
            # cbl_data = computeCBL(data["Hostname"])
            cbl_data = predicted_website_db.find_one(
                {
                    "$or": [
                        {"hostname": data["Hostname"]},
                        {"hostname": data["Hostname"][4:]},
                    ]
                }
            )
            update_cbl_trend_results_daily_scores(
                Trend_Results_db,
                data["ID"],
                cbl_data["predictions"]["probability"] * 10,
                str(DByesterday),
            )
            # updating results db
            Results_db.update_one(
                {"ID": data["ID"]},
                {
                    "$set": {
                        "breach_risk_score": cbl_data["predictions"]["probability"] * 10
                    }
                },
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"breach_Date": str(DByesterday)}}
            )
        else:
            cbl_data = predicted_website_db.find_one({"hostname": data["Hostname"]})

        # overall
        if trend_data["overall_Date"][-1] != str(today):
            cve_data["css_score"] = squish(
                cve_data["css_score"],
                old_css_min,
                old_css_max,
                new_css_min,
                new_css_max,
            )
            cve_data["nvd_score"] = squish(
                cve_data["nvd_score"],
                old_nvd_min,
                old_nvd_max,
                new_nvd_min,
                new_nvd_max,
            )
            # bss_data["BSS"] = squish(bss_data["BSS"])

            overall_score = computeOverallscore(
                bss_data["brand"],
                cve_data["nvd_score"],
                cve_data["css_score"],
                cbl_data["predictions"]["probability"] * 10,
            )
            update_overall_trend_results_daily_scores(
                Trend_Results_db, data["ID"], overall_score, str(DByesterday)
            )
            # updating results db
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"overall_score": overall_score}}
            )
            Results_db.update_one(
                {"ID": data["ID"]}, {"$set": {"overall_Date": str(DByesterday)}}
            )
            i = i + 1
    vendor_updater()


dailyDbUpdater1()
