from common.pipeline.utils import read_config_file

config = read_config_file()

config_datasets = config["datasets"]
DATASETS_PATH = config_datasets["path_to_datasets"]
BUILT_WITH_DATA_LOCATION = DATASETS_PATH + config_datasets["built_with_data"]
EXTERNAL_IDS_LOCATION = DATASETS_PATH + config_datasets["external_ids"]
EXTRACTED_NVD_DATA_LOCATION = DATASETS_PATH + config_datasets["extracted_nvd_data"]
GROUPED_TECHNOLOGIES_LOCATION = DATASETS_PATH + config_datasets["grouped_technologies"]
WEB_TECHNOLOGIES_LOCATION = DATASETS_PATH + config_datasets["web_technologies"]

config_extra_datasets = config["extra_datasets"]
EXTRA_DATASETS_PATH = config_extra_datasets["path_to_datasets"]
DOMAIN_API_JSON_LOCATION = (
    EXTRA_DATASETS_PATH + config_extra_datasets["domain_api_json_location"]
)
BUNDLE_API_JSON_LOCATION = (
    EXTRA_DATASETS_PATH + config_extra_datasets["bundle_api_json_location"]
)

config_output = config["outputs"]
OUTPUT_PATH = config_output["path_to_outputs"]
OUTPUT_COMPANY_SCORE_LOCATION = OUTPUT_PATH + config_output["output_company_score"]

config_paths = config["paths"]
OUTPUT_PATH = config_paths["path_to_Output"]
CSS_PATH = config_paths["path_to_Css_data"]
KEY_PATH = config_paths["path_to_key"]
config_creds = config["credentials"]
config_endpoint = config["endpoints"]
DOMAIN_KEY = config_creds["bw_api_key"]
DOMAIN_URL = config_endpoint["domain"]
TRUST_URL = config_endpoint["trust"]
FREE_URL = config_endpoint["free"]


config_sql_database = config["sql_database"]
config_sql_tables = config_sql_database["tables"]
VENDOR_AND_CLIENT_TABLENAME = config_sql_tables["vendor_and_client_tablename"]
SPECIFIC_COMPANY_DATA = config_sql_tables["specific_company_data_tablename"]
REGISTERED_CLIENT_DATA_TABLENAME = config_sql_tables[
    "registered_client_data_tablename"
]

CLIENT_VENDORS_RELATIONSHIP_FOR_UI_TABLENAME = config_sql_tables[
    "client_vendors_relationship_for_ui_tablename"
]

CYBER_SCHEMA_NAME = config_sql_database['schema_name']

TOP_CVE_DATA_TABLENAME = config_sql_tables[
    "top_cve_data_tablename"
]

NVD_DATA_TABLENAME = config_sql_tables[
    "nvd_data_tablename"
]

RESULT_DATA_TABLENAME = config_sql_tables[
    "result_data_tablename"
]

VENDOR_RISK_DATA_TABLENAME = config_sql_tables[
    "vendor_risk_data_tablename"
]

MODEL_PREDICTED_WEBSITE_FEATURES_DATA_TABLENAME = config_sql_tables[
    "model_predicted_website_features_data_tablename"
]
WEBSITE_API_METADATA_TABLENAME = config_sql_tables[
    "website_api_metadata_tablename"
]
BUNDLE_API_METADATA_TABLENAME = config_sql_tables[
    "bundle_api_metadata_tablename"
]
DOMAIN_API_METADATA_TABLENAME = config_sql_tables[
    "domain_api_metadata_tablename"
]

CLIENT_LOGIN_TABLENAME = config_sql_tables[
    "client_login_tablename"
]

GENERAL_COMPANY_DATA_TABLENAME = config_sql_tables[
    "general_company_data_tablename"
]

COMPANY_DOMAIN_DATA_TABLENAME = config_sql_tables[
    "company_domain_data_tablename"
]
