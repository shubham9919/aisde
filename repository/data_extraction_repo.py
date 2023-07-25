import json

from common.config_constants import DOMAIN_API_JSON_LOCATION, BUNDLE_API_JSON_LOCATION
from common.database.database_utils import (
    insert_data_many,
    domain_api_db,
    bundle_api_db,
    get_all_collections,
)
from common.utils_external import get_all_file_names_from_location


def extract_domain_api_files():
    all_filenames = get_all_file_names_from_location(DOMAIN_API_JSON_LOCATION)
    domain_filenames = [
        file for file in all_filenames if file.endswith("domain_api.json")
    ]
    return domain_filenames


def extract_domain_api_technologies(filenames):
    final_res = []
    seen = set(get_all_collections(domain_api_db).distinct("company"))
    for filename in filenames:
        file = open(DOMAIN_API_JSON_LOCATION + filename, encoding="utf-8")
        data = json.load(file)
        res = dict()
        company_name = data["Results"][0]["Meta"]["CompanyName"]
        res["company"] = (
            company_name.lower()
            if company_name
            else filename[:-16].replace("-", " ").lower()
        )
        res["technologies"] = [
            child["Name"]
            for child in data["Results"][0]["Result"]["Paths"][0]["Technologies"]
        ]
        if res["company"] not in seen:
            seen.add(res["company"])
            final_res.append(res)
    return final_res


def insert_to_domain_api_db():
    new_data = extract_domain_api_technologies(extract_domain_api_files())
    if new_data:
        insert_data_many(domain_api_db, new_data)
        print(f"{len(new_data)} inserted!")
    else:
        print("All Values already present in DB! No New Insertions!")


def extract_bundle_api_files():
    all_filenames = get_all_file_names_from_location(BUNDLE_API_JSON_LOCATION)
    bundle_filenames = [file for file in all_filenames if file.endswith(".json")]
    return bundle_filenames


def extract_bundle_api_technologies(filenames):
    final_res = []
    seen = set(get_all_collections(bundle_api_db).distinct("external_id"))
    for filename in filenames:
        file = open(BUNDLE_API_JSON_LOCATION + filename, encoding="utf-8")
        data = json.load(file)
        for obj in data["objects"]:
            if ("external_references" in obj) and ("x_sixgill_info" in obj):
                res = dict()
                external_id = obj["external_references"][0]["external_id"]
                res["external_id"] = external_id
                res["x_sixgill_score"] = obj["x_sixgill_info"]["score"]
                if external_id not in seen:
                    seen.add(external_id)
                    final_res.append(res)
    return final_res


def insert_to_bundle_api_db():
    new_data = extract_bundle_api_technologies(extract_bundle_api_files())
    if new_data:
        insert_data_many(bundle_api_db, new_data)
        print(f"{len(new_data)} inserted!")
    else:
        print("All Values already present in DB! No New Insertions!")
