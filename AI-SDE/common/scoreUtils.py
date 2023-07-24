from common.tev_utils import tev_pipeline, tev_logger
from common.BSS_utils import bssdatelogger
from common.database.database_utils import (
    Company_db,
    vendor_risk_db,
    Trend_Results_db,
    website_db,
    Company_db,
    top_cve_db,
    domain_api_db,
    predicted_website_db,
    Results_db,
    get_data_from_current_db,
    insert_data_in_db,
    update_data,
    update_tev_trend_results_daily_scores,
    update_bss_trend_results_daily_scores,
    update_cbl_trend_results_daily_scores,
    update_overall_trend_results_daily_scores,
)
from common.api_utils import (
    get_domain_api_data,
    get_website_data_from_api,
    process_data,
)
import datetime
from common.constant_variables import (
    old_bss_max,
    old_bss_min,
    new_bss_max,
    new_bss_min,
    old_css_min,
    old_css_max,
    new_css_min,
    new_css_max,
    old_nvd_min,
    old_nvd_max,
    new_nvd_min,
    new_nvd_max,
)
from common.dataproviderapi import get_searchengine_api_response
from common.api_utils import get_domain_api_data

today = datetime.date.today()

# A function to Normalize scores TEV/BSS 
def squish(
    score,
    old_min=old_bss_min,
    old_max=old_bss_max,
    new_min=new_bss_min,
    new_max=new_bss_max,
):
    new_val = ((score - old_min) / (old_max - old_min) * (new_max - new_min)) + new_min
    return new_val

# A function to compute the overall score
def computeOverallscore(bss, nvd, css, cbl):
    overall = round((bss + nvd + css + cbl) / 4, 2)
    return overall

# computes CBL
def computeCBL(hostname):
    data = get_data_from_current_db(website_db, hostname)
    if data:
        if data["date_executed"] == str(today):
            response_with_features = get_data_from_current_db(
                predicted_website_db, hostname
            )
            if response_with_features is None:
                response_with_features = process_data(data)
                insert_data_in_db(predicted_website_db, response_with_features)
            return response_with_features
        else:
            print("Getting from API")
            response = get_website_data_from_api(hostname)
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
                old_data = get_data_from_current_db(predicted_website_db, hostname)
                new_data = response_with_features
                update_data(predicted_website_db, old_data, new_data)
                return response_with_features
    else:
        print("Getting from API")
        response = get_website_data_from_api(hostname)
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
            insert_data_in_db(predicted_website_db, response_with_features)
            return response_with_features


# computes TEV for new comp
def newTEV(company, hostname, date):
    api_data = dict()
    company = company.lower()
    api_data = get_domain_api_data(hostname, company)
    if api_data is None:
        return None
    domain_api_db.insert_one(api_data)
    tev_data = tev_logger(company, date)
    return tev_data

# compute CBL for new
def newCBL(hostname, date):
    response = get_website_data_from_api(hostname)
    if response["status"] == 200:
        api_data = response["output"]["data"]
        api_data["date_executed"] = date
        insert_data_in_db(website_db, api_data)
        response_with_features = process_data(api_data)
        response_with_features["date_executed"] = date
        if "trustgrade" not in api_data.keys():
            response_with_features["features"]["trustgrade"] = " "
        else:
            response_with_features["features"]["trustgrade"] = api_data["trustgrade"]
        insert_data_in_db(predicted_website_db, response_with_features)
        return response_with_features
    return None

# finding the maximum score
def findMaxScore(CBL, NVD, CSS, BSS):
    if CBL > NVD and CBL > CSS and CBL > BSS:
        return "Breach Risk"
    elif NVD > CBL and NVD > CSS and NVD > BSS:
        return "Dark Web"
    elif CSS > CBL and CSS > NVD and CSS > BSS:
        return "CVE Exposure"
    else:
        return "Sentiment"

# computes BS score
def compute_brandSentimentScore(ID, score):
    trend_data = Trend_Results_db.find_one({"ID": ID})
    initial_bss = trend_data["bss_score"][-1]
    final_bss = score
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

# computes all scores and updates
def computescores(ID):
    comp_data = Company_db.find_one({"ID": ID})
    trend_data = Trend_Results_db.find_one({"ID": ID})
    results_data = Results_db.find_one({"ID": ID})
    res = dict()
    res1 = dict()
    # TEV
    if results_data["nvd_Date"] != str(today) or results_data["css_Date"] != str(today):
        tev_data = tev_pipeline(comp_data["Company"])
        update_tev_trend_results_daily_scores(
            Trend_Results_db,
            comp_data["ID"],
            tev_data["nvd_score"],
            tev_data["css_score"],
            tev_data["Date"],
        )
        # updating results_db
        Results_db.update_one(
            {"ID": ID}, {"$set": {"nvd_score": tev_data["nvd_score"]}}
        )
        Results_db.update_one(
            {"ID": ID}, {"$set": {"css_score": tev_data["css_score"]}}
        )
        Results_db.update_one({"ID": ID}, {"$set": {"nvd_Date": tev_data["Date"]}})
        Results_db.update_one({"ID": ID}, {"$set": {"css_Date": tev_data["Date"]}})
    else:
        res["nvd_score"] = trend_data["nvd_score"][-1]
        res["css_score"] = trend_data["css_score"][-1]
        tev_data = res

    # BSS
    if results_data["bss_Date"] != str(today):
        from_date = results_data["bss_Date"]
        bss_data = bssdatelogger(comp_data["Company"], from_date, str(today))
        bss_data["brand"] = compute_brandSentimentScore(ID, bss_data["BSS"])
        update_bss_trend_results_daily_scores(
            Trend_Results_db,
            comp_data["ID"],
            bss_data["BSS"],
            bss_data["To_Date"],
            bss_data["brand"],
        )
        # updating results db
        Results_db.update_one({"ID": ID}, {"$set": {"bss_score": bss_data["BSS"]}})
        Results_db.update_one({"ID": ID}, {"$set": {"bss_Date": bss_data["To_Date"]}})
        Results_db.update_one({"ID": ID}, {"$set": {"BSS": bss_data["brand"]}})
    else:
        res1["BSS"] = trend_data["brand"][-1]
        bss_data = res1

    # CBL
    if results_data["breach_Date"] != str(today):
        cbl_data = computeCBL(comp_data["Hostname"])  # change the computeCBL func
        update_cbl_trend_results_daily_scores(
            Trend_Results_db,
            comp_data["ID"],
            cbl_data["predictions"]["probability"] * 10,
            cbl_data["date_executed"],
        )
        # updating results db
        Results_db.update_one(
            {"ID": ID},
            {
                "$set": {
                    "breach_risk_score": cbl_data["predictions"]["probability"] * 10
                }
            },
        )
        Results_db.update_one(
            {"ID": ID}, {"$set": {"breach_Date": cbl_data["date_executed"]}}
        )
    else:
        cbl_data = predicted_website_db.find_one({"hostname": comp_data["Hostname"]})

    # Overall
    if results_data["overall_Date"] != str(today):
        tev_data["nvd_score"] = squish(
            tev_data["nvd_score"], old_nvd_min, old_nvd_max, new_nvd_min, new_nvd_max
        )
        tev_data["css_score"] = squish(
            tev_data["css_score"], old_css_min, old_css_max, new_css_min, new_css_max
        )
        # bss_data["BSS"] = squish(bss_data["BSS"])
        overall_score = computeOverallscore(
            bss_data["brand"],
            tev_data["nvd_score"],
            tev_data["css_score"],
            cbl_data["predictions"]["probability"] * 10,
        )
        update_overall_trend_results_daily_scores(
            Trend_Results_db, comp_data["ID"], overall_score, str(today)
        )
        # updating results db
        Results_db.update_one({"ID": ID}, {"$set": {"overall_score": overall_score}})
        Results_db.update_one({"ID": ID}, {"$set": {"overall_Date": str(today)}})

    return Results_db.find_one({"ID": ID})

# compute data for new comp
def new_comp_data_prep(company, hostname):
    comp_data = dict()
    res_dict = dict()
    css_score_list = list()
    bss_score_list = list()
    brand_score_list = list()
    nvd_score_list = list()
    overall_score_list = list()
    breach_score_list = list()
    date_list = list()
    days = 15
    new_ID = Company_db.distinct("ID")[-1] + 1

    # cooking company data
    comp_data["ID"] = new_ID
    comp_data["Company"] = company.lower()
    comp_data["Hostname"] = hostname
    Company_db.insert_one(comp_data)

    # getting data for past 15 days
    for i in range(days + 1):
        from_date = today - datetime.timedelta(days - i + 1)
        to_date = today - datetime.timedelta(days - i)
        tev_data = newTEV(comp_data["Company"], comp_data["Hostname"], str(to_date))
        bss_data = bssdatelogger(comp_data["Company"], str(from_date), str(to_date))
        bss_data["brand"] = compute_brandSentimentScore(new_ID, bss_data["BSS"])
        cbl_data = newCBL(comp_data["Hostname"], str(to_date))
        css_score_list.append(tev_data["css_score"])
        nvd_score_list.append(tev_data["nvd_score"])
        bss_score_list.append(bss_data["BSS"])
        brand_score_list.append(bss_data["brand"])
        breach_score_list.append(cbl_data["predictions"]["probability"] * 10)
        tev_data["nvd_score"] = squish(
            tev_data["nvd_score"], old_nvd_min, old_nvd_max, new_nvd_min, new_nvd_max
        )
        tev_data["css_score"] = squish(
            tev_data["css_score"], old_css_min, old_css_max, new_css_min, new_css_max
        )
        # bss_data["BSS"] = squish(bss_data["BSS"])
        overall_score = computeOverallscore(
            bss_data["brand"],
            tev_data["nvd_score"],
            tev_data["css_score"],
            cbl_data["predictions"]["probability"] * 10,
        )
        overall_score_list.append(overall_score)
        date_list.append(str(to_date))
    res_dict["ID"] = new_ID
    res_dict["nvd_score"] = nvd_score_list
    res_dict["nvd_Date"] = date_list
    res_dict["css_score"] = css_score_list
    res_dict["css_Date"] = date_list
    res_dict["overall_score"] = overall_score_list
    res_dict["overall_Date"] = date_list
    res_dict["breach_risk_score"] = breach_score_list
    res_dict["breach_Date"] = date_list
    res_dict["bss_score"] = bss_score_list
    res_dict["bss_date"] = date_list
    res_dict["BSS"] = brand_score_list
    Trend_Results_db.insert_one(res_dict)

    res_dict["ID"] = new_ID
    res_dict["nvd_score"] = nvd_score_list[-1]
    res_dict["nvd_Date"] = date_list[-1]
    res_dict["css_score"] = css_score_list[-1]
    res_dict["css_Date"] = date_list[-1]
    res_dict["overall_score"] = overall_score_list[-1]
    res_dict["overall_Date"] = date_list[-1]
    res_dict["breach_risk_score"] = breach_score_list[-1]
    res_dict["breach_Date"] = date_list[-1]
    res_dict["bss_score"] = bss_score_list[-1]
    res_dict["bss_Date"] = date_list[-1]
    res_dict["BSS"] = brand_score_list[-1]
    res_dict.pop("bss_date")
    Results_db.insert_one(res_dict)
    return new_ID

# A function to get the resultant dict data for UI - For now this fucnction does not actively compute scores from new dates (No API access for )
def res_dict(company, hostname, data_mode, ID):
    result = dict()
    # checking results_db for fresh data
    data = Results_db.find_one({"ID": ID})
    # temp code to get dataprovider api data for web ui entries
    # if data["breach_Date"] != str(today):
    #     cbl = computeCBL(hostname)
    #     Results_db.update_one(
    #         {"ID": ID},
    #         {"$set": {"breach_risk_score": cbl["predictions"]["probability"] * 10}},
    #     )
    #     Results_db.update_one({"ID": ID}, {"$set": {"breach_Date": str(today)}})
    #     Trend_Results_db.update_one(
    #         {"ID": ID},
    #         {
    #             "$push": {
    #                 "breach_risk_score": cbl["predictions"]["probability"] * 10
    #             }
    #         },
    #     )
    #     Trend_Results_db.update_one(
    #         {"ID": ID}, {"$push": {"breach_Date": str(today)}}
    #     )
    # data = Results_db.find_one({"ID": ID})
    comp_data = Company_db.find_one({"ID": ID})

    # data = Results_db.find_one({"ID": ID})
    # comp_data = Company_db.find_one({"ID": ID})

    # just give the present data
    if data_mode == 0:
        result_data = data

    # check for new data
    else:
        if (
            data["nvd_Date"] != str(today)
            or data["css_Date"] != str(today)
            or data["bss_Date"] != str(today)
            or data["breach_Date"] != str(today)
            or data["overall_Date"] != str(today)
        ):
            result_data = computescores(ID)
        else:
            result_data = data
    trend_data = Trend_Results_db.find_one({"ID": ID})

    # making all scores scale to 10
    # result_data["bss_score"] = result_data["brand"]

    result_data["nvd_score"] = squish(
        result_data["nvd_score"], old_nvd_min, old_nvd_max, new_nvd_min, new_nvd_max
    )

    result_data["css_score"] = squish(
        result_data["css_score"], old_css_min, old_css_max, new_css_min, new_css_max
    )
    pred_web_data = predicted_website_db.find_one(
        {
            "$or": [
                {"hostname": comp_data["Hostname"]},
                {"hostname": comp_data["Hostname"][4:]},
            ]
        }
    )

    # preparing data
    initialo = trend_data["overall_score"][-2]
    finalo = trend_data["overall_score"][-1]
    initialb = trend_data["breach_risk_score"][-2]
    finalb = trend_data["breach_risk_score"][-1]
    initialbss = trend_data["bss_score"][-2]
    finalbss = trend_data["bss_score"][-1]
    initialcss = trend_data["css_score"][-2]
    finalcss = trend_data["css_score"][-1]

    # adding all values into a single dict
    result["BSS_trend"] = trend_data["bss_score"]
    result["CVEG_nvd_score"] = trend_data["nvd_score"]
    result["CVEG_css_score"] = trend_data["css_score"]
    result["Overall"] = result_data["overall_score"]
    result["Breach_Risk_Score"] = trend_data["breach_risk_score"]
    result["overall_trend"] = trend_data["overall_score"]
    result["predictions"] = pred_web_data["predictions"]
    result["features"] = pred_web_data["features"]
    result["BSS"] = result_data["BSS"]
    result["success"] = pred_web_data["success"]
    result["CVE"] = list(top_cve_db.find({}))
    if initialo == 0:
        result["overall_inc"] = (finalo - initialo) / 1
    else:
        result["overall_inc"] = (finalo - initialo) / abs(initialo)
    if initialb == 0:
        result["breach_inc"] = (finalb - initialb) / 1
    else:
        result["breach_inc"] = (finalb - initialb) / abs(initialb)
    if initialbss == 0:
        result["bss_inc"] = (finalbss - initialbss) / 1
    else:
        result["bss_inc"] = (finalbss - initialbss) / abs(initialbss)
    if initialcss == 0:
        result["css_inc"] = (finalcss - initialcss) / 1
    else:
        result["css_inc"] = (finalcss - initialcss) / abs(initialcss)
    return result

# updates vendor scores
def vendor_updater():
    ids = vendor_risk_db.distinct("ID")
    for item in ids:
        res = dict()
        comp = Company_db.find_one({"ID": item})
        if (
            comp["Company"] == "meta"
            or comp["Company"] == "samsung"
            or comp["Company"] == "microsoft"
        ):
            continue
        res_data = Results_db.find_one({"ID": item})
        res["ID"] = item
        res["Company"] = comp["Company"]
        web_data = website_db.find_one(
            {"$or": [{"hostname": comp["Hostname"]}, {"domain": comp["Hostname"]}]}
        )
        if web_data is None:
            continue
        if web_data["domain"] is None:
            res["Domain"] = "Unknown"
        res["Domain"] = web_data["domain"]
        if "sicdivision" not in web_data.keys():
            res["Industry"] = "Unknown"
        else:
            res["Industry"] = web_data["sicdivision"]
        if res_data["overall_score"] > 6.0 and res_data["overall_score"] <= 9.0:
            res["Status"] = "High"
        elif res_data["overall_score"] > 3.0 and res_data["overall_score"] <= 6.0:
            res["Status"] = "Medium"
        elif res_data["overall_score"] > 0.0 and res_data["overall_score"] <= 3.0:
            res["Status"] = "Low"
        else:
            res["Status"] = "Critical"
        print(res["Status"])
        res_data["nvd_score"] = squish(
            res_data["nvd_score"], old_nvd_min, old_nvd_max, new_nvd_min, new_nvd_max
        )
        res_data["css_score"] = squish(
            res_data["css_score"], old_css_min, old_css_max, new_css_min, new_css_max
        )
        res_data["bss_score"] = squish(res_data["bss_score"])

        res["Alert_Type"] = findMaxScore(
            res_data["breach_risk_score"],
            res_data["nvd_score"],
            res_data["css_score"],
            res_data["bss_score"],
        )
        res["Date"] = str(today)

        vendor_risk_db.update_one({"ID": item}, {"$set": {"Status": res["Status"]}})
        vendor_risk_db.update_one(
            {"ID": item}, {"$set": {"Alert_Type": res["Alert_Type"]}}
        )

# check if all the api can give response for a given company and hostname
def api_checker(company, hostname):
    cbl_data, status_code = get_searchengine_api_response(hostname)
    if status_code != 200:
        return None
    tev_data = get_domain_api_data(hostname, company)
    if tev_data is None:
        return None
    return True
