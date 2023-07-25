import json

import requests


#########################
# Bearer Token          #
#########################
def get_post_bearer_token():
    """
    Post request on for authentication token.
    Valid for 60 minutes (3600 seconds).

    Parameters:
    headers (dict): format params required by endpoint
    payload (json): authorization parameters

    Returns:
    access_token (str): properly formated token
    """

    headers = {
        "Accept": "application/vnd.api.v1+json",
        "Content-Type": "application/json",
    }

    payload = json.dumps(json.load(open("config/vault.json")))

    url = "https://api.dataprovider.com/v2/auth/oauth2/token"
    r = requests.post(url, headers=headers, data=payload)

    try:
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        return err, r.status_code

    # if no error raised
    response_obj = r.json()
    access_token = "Bearer " + response_obj["access_token"]
    refresh_token = response_obj["refresh_token"]
    return access_token, refresh_token


#########################
# Get Search Engine     #
#########################
def get_searchengine_api_response(hostname, payload=None):
    """
    Get request on dataprovider search engine api for info on domain.
    Calls save_json_local().

    Parameters:
    hostname (string): web url for company
    headers (dict):  format params required by endpoint & authorization token
    payload (json): query parameters if desired

    Returns:
    response (json): DataProvider Search Engine endpoint response
    """
    access_token, refresh_token = get_post_bearer_token()
    headers = {
        "Accept": "application/vnd.api.v1+json",
        "Content-Type": "application/json",
        "Authorization": access_token,
    }

    search_url = "https://api.dataprovider.com/v2/search-engine/hostnames/" + hostname
    r = requests.get(search_url, headers=headers, data=payload)
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        return err, r.status_code

    response = r.json()
    return response, r.status_code
