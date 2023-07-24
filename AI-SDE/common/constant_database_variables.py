OUTPUT_RESULTS_COLUMN_SPECIFIC_CLIENT = [
    "nvd_score",
    "css_score",
    "master_score",
    "breach_risk_score",
    "bss_score",
    "bss",
]

OUTPUT_RESULTS_COLUMN_SPECIFIC_CLIENT_WITH_DOMAIN_NAMES = [
    "company_name",
    "domain_name",
    "nvd_score",
    "css_score",
    "master_score",
    "breach_risk_score",
    "bss_score",
    "bss",
]

UPLOAD_DC_CSV_REQUIRED_COLS = ["company", "domain", "technologies"]

UPLOAD_ENTERPRISE_VENDORS_CSV_REQUIRED_COLS = [
    "enterprise",
    "enterprise_domain",
    "vendor",
    "vendor_domain",
    "technologies",
]


OUTPUT_FEATURES_COLUMN_SPECIFIC_CLIENT = [
    "technologies"
]

OUTPUT_FEATURES_COLUMN_SPECIFIC_CLIENT_WITH_DOMAIN_NAMES = [
    "company_name",
    "domain_name",
    "technologies",
]