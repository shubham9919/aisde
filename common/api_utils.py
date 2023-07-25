from datetime import date
import requests
import pandas as pd
from common.config_constants import DOMAIN_KEY, DOMAIN_URL, TRUST_URL, FREE_URL
from common.dataproviderapi import get_searchengine_api_response
from common.enums import StageType
from common.pipeline.utils import perform_feature_selection
from prediction.prediction_repository import MakePredictionsFlask
import re

# function to process CBL data
def process_data(data):
    response_with_features = process_keys(data)
    predictions = making_predictions(response_with_features["features"])
    response_with_features["predictions"] = predictions
    response_with_features["hostname"] = response_with_features["features"]["hostname"]
    response_with_features["date_executed"] = str(date.today())
    return response_with_features


# function to retrieve website data from API
def get_website_data_from_api(req):
    data, status_code = get_searchengine_api_response(req)
    if status_code == 200:
        data["data"]["status"] = status_code
        return {"output": data, "status": status_code}
    else:
        new_data = dict()
        new_data["data"] = dict()
        new_data["data"]["status"] = status_code
        new_data["data"]["features"] = dict()
        new_data["data"]["success"] = False
        new_data["data"]["features"]["hostname"] = req
        return {"output": new_data, "status": status_code}


# function to process the retrieved website data and to process it for the model input
def process_keys(req):
    final_data = dict()
    final_data["features"] = dict()
    final_data["success"] = True
    final_data["features"]["company"] = req.get(
        "company", "Company key not found in API"
    )
    final_data["features"]["hostname"] = req.get("hostname")
    final_data["features"]["loadtime"] = req.get("loadtime", 0)
    final_data["features"]["changes"] = req.get("changes", 0)
    final_data["features"]["cloudscore"] = req.get("cloudscore", 0)
    final_data["features"]["domainlength"] = req.get("domainlength", 0)
    final_data["features"]["eii"] = req.get("eii", 0)
    final_data["features"]["forwardingcount"] = req.get("forwardingcount", 0)
    final_data["features"]["htmlsize"] = req.get("htmlsize", 0)
    final_data["features"]["incominglinks"] = req.get("incominglinks", 0)
    final_data["features"]["subdomainscount"] = req.get("subdomainscount", 0)
    final_data["features"]["outgoinglinks"] = req.get("outgoinglinks", 0)
    final_data["features"]["pagesindexed"] = req.get("pagesindexed", 0)
    final_data["features"]["pages"] = req.get("pages", 0)
    final_data["features"]["seo"] = req.get("seo", 0)
    final_data["features"]["trustscore"] = req.get("trustscore", 0)
    final_data["features"]["securityscore"] = req.get("securityscore", 0)
    final_data["features"]["visitorsavg"] = req.get("visitorsavg", 0)
    final_data["features"]["visitors"] = req.get("visitors", 0)
    final_data["features"]["grade"] = req.get("grade", 0)
    final_data["features"]["trustgrade"] = req.get("trustgrade", 0)
    final_data["features"]["trafficindex"] = req.get("trafficindex", 0)
    final_data["features"]["trustscore"] = req.get("trustscore", 0)
    final_data["features"]["websiteage"] = req.get("websiteage", 0)
    final_data["features"]["ecommercequality"] = req.get("ecommercequality", 0)
    return final_data


# A utility function for making predictions
def making_predictions(req):
    company = req["company"]
    hostname = req["hostname"]
    dp_average_load_time_ms = req["loadtime"]
    dp_changes = req["changes"]
    dp_cloud_score = req["cloudscore"]
    dp_domain_name_length = req["domainlength"]
    dp_economic_footprint = req["eii"]
    dp_forwarding_domains_count = req["forwardingcount"]
    dp_html_size_kb = req["htmlsize"]
    dp_incoming_links = req["incominglinks"]
    dp_linked_subdomains_count = req["subdomainscount"]
    dp_outgoing_links = req["outgoinglinks"]
    dp_pages_indexed = req["pagesindexed"]
    dp_pages = req["pages"]
    dp_seo_score = req["seo"]
    dp_score = req["trustscore"]
    dp_security_score = req["securityscore"]
    dp_site_traffic_estimation_average = req["visitorsavg"]
    dp_site_traffic_estimation = req["visitors"]
    dp_technical_evaluation = req["grade"]
    dp_traffic_index = req["trafficindex"]
    dp_trust_score = req["trustscore"]
    dp_website_age = req["websiteage"]
    dp_ecommerce_certainty = req["ecommercequality"]

    data = [
        [
            company,
            hostname,
            dp_average_load_time_ms,
            dp_changes,
            dp_cloud_score,
            dp_domain_name_length,
            dp_economic_footprint,
            dp_forwarding_domains_count,
            dp_html_size_kb,
            dp_incoming_links,
            dp_linked_subdomains_count,
            dp_outgoing_links,
            dp_pages_indexed,
            dp_pages,
            dp_seo_score,
            dp_score,
            dp_security_score,
            dp_site_traffic_estimation_average,
            dp_site_traffic_estimation,
            dp_technical_evaluation,
            dp_traffic_index,
            dp_trust_score,
            dp_website_age,
            dp_ecommerce_certainty,
        ]
    ]

    column_names = [
        "company",
        "hostname",
        "dp_average_load_time_ms",
        "dp_changes",
        "dp_cloud_score",
        "dp_domain_name_length",
        "dp_economic_footprint",
        "dp_forwarding_domains_count",
        "dp_html_size_kb",
        "dp_incoming_links",
        "dp_linked_subdomains_count",
        "dp_outgoing_links",
        "dp_pages_indexed",
        "dp_pages",
        "dp_seo_score",
        "dp_score",
        "dp_security_score",
        "dp_site_traffic_estimation_average",
        "dp_site_traffic_estimation",
        "dp_technical_evaluation",
        "dp_traffic_index",
        "dp_trust_score",
        "dp_website_age",
        "dp_ecommerce_certainty",
    ]

    as_int_columns = [
        "dp_average_load_time_ms",
        "dp_changes",
        "dp_cloud_score",
        "dp_domain_name_length",
        "dp_economic_footprint",
        "dp_forwarding_domains_count",
        "dp_html_size_kb",
        "dp_incoming_links",
        "dp_linked_subdomains_count",
        "dp_outgoing_links",
        "dp_pages_indexed",
        "dp_pages",
        "dp_seo_score",
        "dp_score",
        "dp_security_score",
        "dp_site_traffic_estimation_average",
        "dp_site_traffic_estimation",
        "dp_technical_evaluation",
        "dp_traffic_index",
        "dp_trust_score",
        "dp_website_age",
        "dp_ecommerce_certainty",
    ]

    stage_type = StageType.START_PREDICTIONS
    df = pd.DataFrame(data=data, columns=column_names)
    df[as_int_columns] = df[as_int_columns].astype(int)
    # df = data_cleaning(df, stage_type)
    df = perform_feature_selection(df, stage_type)
    pred_prob, pred_class = MakePredictionsFlask(df).get_preds()
    result = dict()
    result["probability"] = round(float(pred_prob), 2)
    result["class"] = int(pred_class)
    return result


# function to get builtwith domain api info on domain
def get_domain_api(domain):
    """
    Get request on builtwith domain api for info on domain.

    Parameters:
    domain (string): web url for company

    Returns:
    None
    """
    domain_url = DOMAIN_URL
    try:
        r = requests.get(domain_url + domain)
    except requests.exceptions.RequestException as err:
        return "Response Error: " + str(err)
    domain_response = r.json()
    return domain_response


# function to extract tech from a json
def extract_tech(data):
    Technologies = []
    # unwinding list of dictionaries
    result = dict()
    result = data["Results"][0]
    result2 = dict()
    result2 = result["Result"]["Paths"][0]

    # Extracting technology words
    for obj in result2["Technologies"]:
        if "Name" in obj:
            Technologies.append(obj["Name"].lower())

    return Technologies


# function to extract technology data from builtwith data
def get_domain_api_data(domain, company):
    data = get_domain_api(domain)
    # if not data address
    if data is None:
        return None
    tech = extract_tech(data)
    tev_dict = dict()
    tev_dict["company"] = company
    tev_dict["technologies"] = tech
    return tev_dict


# function to verify validity of a domain
def is_valid_domain(str):
    """
    Verify valid domain name
    """
    regex = "^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}$"
    # (?!-)                 not starting with (-)
    # [A-Za-z0-9-]{1,63}    letters and numbers to a max of 63 chars
    # (?<!-)                not ending with (-)
    # [A-Za-z]{2,6}         letters for top level domain 2-6 chars

    p = re.compile(regex)

    # catch empty string
    if str == None:
        return False

    # Return True if the string matched the regex
    if re.search(p, str):
        return True
    return False


# function to get builtwith trust api for info on domain
def get_trust_api(domain):
    """
    Get request on builtwith trust api for info on domain.
    Calls save_json_local().
    # Status:
    # * 0 = ok
    # * 1 = suspect
    # * 2 = needLive #specify &LIVE=yes in request url

    Parameters:
    domain (string): web url for company

    Returns:
    json response
    """
    trust_url = TRUST_URL
    try:
        r = requests.get(trust_url + domain)
    except requests.exceptions.RequestException as err:
        return "Response Error: " + str(err)
    trust_response = r.json()
    return trust_response


# Function to get builtwith free api for info on domain
def get_free_api(domain):
    """
    Get request on builtwith free api for info on domain.
    Provides last updated and counts for technology groups and categories for websites.
    Calls save_json_local().

    Parameters:
    domain (string): web url for company

    Returns:
    json response
    """
    free_url = FREE_URL
    try:
        r = requests.get(free_url + domain)
    except requests.exceptions.RequestException as err:
        return "Response Error: " + str(err)
    free_response = r.json()
    return free_response
