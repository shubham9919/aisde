from common.dataproviderapi import get_searchengine_api_response


company_hostname = "www.twitch.tv"

response = get_searchengine_api_response(company_hostname)

print(response)
