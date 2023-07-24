import datetime
from datetime import timedelta
import json
from typing import List
import time
from common.constant_variables import TOTAL_GROUP_MULTIPLIER
from common.config_constants import (
    BUILT_WITH_DATA_LOCATION,
    EXTERNAL_IDS_LOCATION,
    WEB_TECHNOLOGIES_LOCATION,
    GROUPED_TECHNOLOGIES_LOCATION,
    OUTPUT_COMPANY_SCORE_LOCATION,
)
from common.database.database_utils import (
    domain_api_db,
    NVD_db,
    get_all_collections,
    bundle_api_db,
    predicted_scores_db,
    insert_data_many,
)
from common.enums import PipelineType

today = datetime.date.today()
yesterday = today - timedelta(1)
daybefore = today - timedelta(2)
daybefore1 = today - timedelta(2)

# Function to retrieve company_name details from the preprocessed builtwith data (json)
def get_company_details_from_json(company_name: str) -> List[str]:
    """
    Input:
        - company_name: Name of the company_name
    Output: returns a list of all the technologies associated to it.
    """
    f = open(BUILT_WITH_DATA_LOCATION, encoding="utf8")
    data = json.load(f)
    try:
        tech_list = data[company_name]
    except Exception:
        raise ValueError("company_name name not found!")
    return [x.lower() for x in tech_list]


# Function to retrieve company_name details from the preprocessed builtwith data (MongoDb)
def get_company_details_from_db(company_name):
    """
    Input:
        - company_name: Name of the company_name
    Output: returns a list of all the technologies associated to it.
    """
    company_name = company_name.lower()
    data = domain_api_db.find_one({"company": company_name})
    tech_list = data["technologies"]
    if not tech_list:
        print("No tech found")
        return None
    return [x.lower() for x in tech_list]


# Function to retrieve Trending cve IDs from the preprocessed trend data (json)
def get_trending_ids_from_json() -> List[str]:
    """
    Input - None
    Output - Returns all the cve id's from the trend data
    - IDs
    """
    ids = []
    f = open(EXTERNAL_IDS_LOCATION, encoding="utf8")
    data = json.load(f)
    for item in data.keys():
        ids.append(item)
    f.close()
    return [x.upper() for x in ids]


# Function to retrieve Trending cve IDs from the preprocessed trend data (MongoDB)
def get_trending_ids_from_db() -> List[str]:
    """
    Function to retrieve Trending cve IDs from the preprocessed trend data
    Input - None
    Output - Returns all the cve id's from the trend data
    - IDs
    """
    ids = set(get_all_collections(bundle_api_db).distinct("external_id"))
    return [x.upper() for x in ids]


# Function to get matching CVE IDs from NVD when trend_ids are given
def get_matching_nvd_ids(trend_id):

    """
    This function gets all the trending ID's compares them
    with the extracted NVD database and returns the common cve
    ID's and their scores and technology associated.
    Input: a list of trending id's
        - trend_id

    Output: Three lists of matched cve id's, their technol
    ogies and scores
        -match_id, KeywordList, scores_list, link_list

    """
    keyword_list = []
    final_keyword_list = []

    # code for getting from DB
    nvd_id = NVD_db.distinct("CVE")
    res = list(set(nvd_id).intersection(trend_id))
    for item in res:
        data = NVD_db.find_one({"CVE": item})
        if not data:
            continue
        keyword_list.append(data["technologies"])

    for items in keyword_list:
        if not items:
            continue
        for item in items:
            final_keyword_list.append(item)

    return final_keyword_list


# This Function gets two lists of technologies and returns the common technologies between them
def compare_technologies(list1, list2):
    """
    Input: Two lists to compare and return the common items
        - list1, list2
    Output: A list with all the common entries.
        - risky_techs
    """
    # todo
    risky_techs = [item for item in list1 if item in list2]
    return risky_techs


# function to find CVE IDs at risk for a company from NVD data
def get_cve_ids_at_risk(tech_at_risk):
    """
    This Function gets a list of technologies, searches the preprocessed NVD json for all the
    cve ids and their scores which have at least one technology common.
    Input: Accepts a list of technologies to compare it with Extracted NVD data
        - tech_at_risk
    Output: Two lists, first is all the common cve id's and other is their scores.
        - Ids_at_risk, scores
    """
    # todo
    ids_at_risk = []
    # all documents with at least 1 element in technologies
    nvd_data = list(NVD_db.find({"technologies.0": {"$exists": True}}))
    for item in nvd_data:
        if len(list(set(item["technologies"]).intersection(tech_at_risk))) > 0:
            ids_at_risk.append(item["CVE"])

    return ids_at_risk


# function to find common CVE IDs at risk for a company
def get_common_cve_ids(ids_at_risk):
    """
    This Function gets a list of cve ID's, searches the preprocessed ExternalIDs json for all the common
    cve ids and their scores.
    Input: Accepts a list of cve ID's to compare it with cve ids in ExternalIDs data
        - ids_at_risk
    Output: Two lists, first is all the common cve id's and other is their scores.
        - common_ids, external_score
    """
    # todo
    common_ids = []
    for item in ids_at_risk:
        data = bundle_api_db.find_one({"external_id": item})
        if not data:
            continue
        common_ids.append(item)

    return common_ids


def find_tech_associated(ids):
    """
    This Function gets all the technologies for given list of cve ids
    Input: Accepts a list of cve ID's to compare it with cve ids in Extracted_NVD_Data
        - ids
    Output: A list of technologies for the given cve IDs from Extracted_NVD_Data.
        - tech_associated
    """
    # todo
    tech_associated = []
    res = dict()
    for item in ids:
        data = NVD_db.find_one({"CVE": item})
        res[data["CVE"]] = list(set(data["technologies"]))
        tech_associated.append(res)
    # f = open(EXTRACTED_NVD_DATA_LOCATION, encoding="utf8")
    # data = json.load(f)

    # for item in data.keys():
    #     if item in ids:
    #         tech_associated.append(data[item][0])
    return tech_associated


# A function to compute TEV(NVD/CSS) scores.
def find_tev_score():
    """
    This Function reads the Output.json file and finds the TEV score.
    Output: Prints the NVD and CSV scores from the output file.
        - tech_associated
    """
    # todo
    f = open(OUTPUT_COMPANY_SCORE_LOCATION, encoding="utf8")
    # returns JSON object as a dictionary
    data = json.load(f)
    hashmap = {}
    for index, (key, value) in enumerate(data.items()):
        if index > 1:
            for val in value[-1]:
                if "BasescoreV3" in list(value[0].keys()):
                    base_score = value[0]["BasescoreV3"]
                elif "BasescoreV2" in list(value[0].keys()):
                    base_score = value[0]["BasescoreV2"]
                else:
                    raise ValueError("BasescoreV3 and BasescoreV2 not found")
                current_score = value[1]["current"] if value[1]["current"] else 0
                hashmap[key] = [base_score, current_score, value[-1]]
    f.close()
    # getting group values
    f = open(WEB_TECHNOLOGIES_LOCATION, encoding="utf8")
    g = open(GROUPED_TECHNOLOGIES_LOCATION, encoding="utf8")
    data1 = json.load(f)
    data2 = json.load(g)
    group_list = []
    big_group = dict()
    for item in hashmap.keys():
        tech_list = hashmap[item][-1]

        for j in tech_list:
            for item1 in data1.keys():
                if type(data1[item1]) == list:
                    if j in data1[item1]:
                        for grp in data2.keys():
                            if item1 in data2[grp][0]:
                                group_list.append(data2[grp][1])
                else:
                    for k, v in data1[item1].items():
                        for i in range(len(v)):
                            v[i] = v[i].lower()
                        if j in v:
                            for grp in data2.keys():
                                if item1 in data2[grp][0]:
                                    big_group[j] = data2[grp][1]
                                    group_list.append(data2[grp][1])

    nvd_scores = []
    csv_scores = []
    total_nvd, total_css = 0, 0
    total_multiplier = 1
    temp = list()
    for item in hashmap.keys():
        group_multiplier = 0
        for tech in hashmap[item][-1]:
            if tech not in big_group.keys():
                continue
            temp.append(big_group[tech])
        if len(temp) > 0:
            group_multiplier = max(temp)
        else:
            group_multiplier = total_multiplier
        nvd_scores.append(group_multiplier * hashmap[item][0])
        csv_scores.append(group_multiplier * hashmap[item][1])
        total_multiplier += group_multiplier
    for i in range(len(nvd_scores)):
        total_nvd += nvd_scores[i] / total_multiplier
        total_css += csv_scores[i] / total_multiplier
    f.close()
    g.close()
    return round(total_nvd, 2), round(total_css, 2)


# a function to find TEV scores for a company
def tev_pipeline(company_name, pipeline=PipelineType.DB_PIPELINE):
    start_time = time.time()
    if pipeline == PipelineType.DB_PIPELINE:
        comp_tech_list = get_company_details_from_db(company_name)
        trend_id = get_trending_ids_from_db()

    else:
        comp_tech_list = get_company_details_from_json(company_name)
        trend_id = get_trending_ids_from_json()

    tech_at_risk = get_matching_nvd_ids(trend_id)
    tech_at_risk = set(tech_at_risk)
    common_tech_at_risk = compare_technologies(tech_at_risk, comp_tech_list)
    ids_at_risk = get_cve_ids_at_risk(set(common_tech_at_risk))
    cve = get_common_cve_ids(ids_at_risk)
    cve = list(set(cve))
    tech_associated = find_tech_associated(cve)
    res = {
        "company_name": company_name,
        "technologies_at_risk": list(set(common_tech_at_risk)),
    }
    for cve_id in cve:
        nvd_data = NVD_db.find_one({"CVE": cve_id})
        css_data = bundle_api_db.find_one({"external_id": cve_id})
        for record in tech_associated:
            if cve_id in record.keys():
                tech = record[cve_id]
        res[cve_id] = (
            nvd_data["scores"],
            css_data["x_sixgill_score"],
            nvd_data["link"],
            tech,
        )

    with open(OUTPUT_COMPANY_SCORE_LOCATION, "w") as fp:
        json.dump(res, fp, indent=4)
    total_nvd, total_css = find_tev_score()
    result = dict()
    res_db = dict()
    for item in res.keys():
        if item == "company_name" or item == "technologies_at_risk":
            continue
        else:
            result[item] = res[item]
    res_db["company_name"] = company_name
    res_db["nvd_score"] = total_nvd
    res_db["css_score"] = total_css
    res_db["Date"] = str(yesterday)
    res_db["output"] = result
    print("--- %s seconds ---" % (time.time() - start_time))
    return res_db


# a function to find TEV score for mutiple companies
def tev_pipeline_all_companies():
    all_companies = domain_api_db.distinct("company")
    final_res = []
    for company in all_companies:
        final_res.append(tev_pipeline(company, False))

    insert_data_many(predicted_scores_db, final_res)

    print(
        f"Predicted Scores for {len(all_companies)} companies and saved to predicted_scores_db DB!"
    )


# a function to find TEV score for a company for a particular date
def tev_logger(company_name, date):

    comp_tech_list = get_company_details_from_db(company_name)
    trend_id = get_trending_ids_from_db()

    tech_at_risk = get_matching_nvd_ids(trend_id)
    tech_at_risk = set(tech_at_risk)
    common_tech_at_risk = compare_technologies(tech_at_risk, comp_tech_list)
    ids_at_risk = get_cve_ids_at_risk(set(common_tech_at_risk))
    cve = get_common_cve_ids(ids_at_risk)
    cve = list(set(cve))
    tech_associated = find_tech_associated(cve)
    res = {
        "company_name": company_name,
        "technologies_at_risk": list(set(common_tech_at_risk)),
    }
    for cve_id in cve:
        nvd_data = NVD_db.find_one({"CVE": cve_id})
        css_data = bundle_api_db.find_one({"external_id": cve_id})
        for record in tech_associated:
            if cve_id in record.keys():
                tech = record[cve_id]
        res[cve_id] = (
            nvd_data["scores"],
            css_data["x_sixgill_score"],
            nvd_data["link"],
            tech,
        )

    with open(OUTPUT_COMPANY_SCORE_LOCATION, "w") as fp:
        json.dump(res, fp, indent=4)
    total_nvd, total_css = find_tev_score()
    result = dict()
    res_db = dict()
    for item in res.keys():
        if item == "company_name" or item == "technologies_at_risk":
            continue
        else:
            result[item] = res[item]

    res_db["nvd_score"] = total_nvd
    res_db["css_score"] = total_css
    res_db["Date"] = str(date)
    res_db["output"] = result
    return res_db
