import datetime
import pandas as pd
from common.api_utils import get_domain_api, get_free_api, get_trust_api
from common.api_utils import is_valid_domain

###################################
# Value Calculation Functions     #
###################################

# Function to calculate Sales Revenue
def calculate_sr_value(sales_revenue):
    """
    Calculate scoring value from sales_revenue
    Can be 4, 8, 12, 16, or 20
    """
    sr = 0
    if sales_revenue < 5000000:
        sr = 4
    elif 5000000 <= sales_revenue < 10000000:
        sr = 8
    elif 10000000 <= sales_revenue < 500000000:
        sr = 12
    elif 500000000 <= sales_revenue < 1000000000:
        sr = 16
    elif sales_revenue >= 1000000000:
        sr = 20
    return int(sr)

# not used yet
def years_since_first_indexed(first_indexed):
    """
    Calculate number of years since first indexed.

    Input: (int) first_indexed - unix timestamp (ms)

    Output: (int) years_elapsed - number of years rounded to 3 decimal places
    """
    # convert unix timestamp to datetime
    date = pd.to_datetime(first_indexed, unit="ms")
    now = datetime.datetime.now()
    elapsed = now - date

    # 365.25 days in a year will include leap years as time goes on
    year_in_seconds = 365.25 * 24 * 60 * 60  # = 31,557,600 seconds in 1 year

    years_elapsed = round(elapsed.total_seconds() / year_in_seconds, 3)
    return years_elapsed

# Function to compute MJ Rank (Majestic Rank)
def calculate_mj_value(mj_rank):
    """
    Calculate scoring value from mj_rank
    Can be 1-5
    """
    mj = 0
    if mj_rank < 100:
        mj = 1
    elif 100 <= mj_rank < 1000:
        mj = 2
    elif 1000 <= mj_rank < 10000:
        mj = 3
    elif 10000 <= mj_rank < 500000:
        mj = 4
    elif mj_rank >= 500000:
        mj = 5
    return int(mj)

# Function to compute MJ TLD Rank (Majestic Top Level Domain Rank)
def calculate_mjtld_value(mjtld_rank):
    """
    Calculate scoring value from mjtld_rank
    Can be 1-5
    """
    mjtld = 0
    if mjtld_rank < 100:
        mjtld = 1
    elif 100 <= mjtld_rank < 1000:
        mjtld = 2
    elif 1000 <= mjtld_rank < 10000:
        mjtld = 3
    elif 10000 <= mjtld_rank < 500000:
        mjtld = 4
    elif mjtld_rank >= 500000:
        mjtld = 5
    return int(mjtld)

# Function to compute Ref SN (Referring Subnets)
def calculate_refsn_value(ref_sn):
    """
    Calculate scoring value from ref_sn
    Can be 1-5
    """
    sn = 0
    if ref_sn < 100:
        sn = 1
    elif 100 <= ref_sn < 500:
        sn = 2
    elif 500 <= ref_sn < 10000:
        sn = 3
    elif 10000 <= ref_sn < 50000:
        sn = 4
    elif ref_sn >= 50000:
        sn = 5
    return int(sn)

# Function to compute Ref IP (Referring IP's)
def calculate_refip_value(ref_ip):
    """
    Calculate scoring value from ref_ip
    Can be 1-5
    """
    ip = 0
    if ref_ip < 100:
        ip = 1
    elif 100 <= ref_ip < 1000:
        ip = 2
    elif 1000 <= ref_ip < 10000:
        ip = 3
    elif 10000 <= ref_ip < 100000:
        ip = 4
    elif ref_ip >= 100000:
        ip = 5
    return int(ip)

# Function to compute Payment Options
def calculate_payment_options_value(payment_options):
    """
    Calculate scoring value from payment_options
    Can be 0 or 20
    """
    po = 0
    if payment_options:
        po = 20
    return int(po)

# Function to compute Ecommerce
def calculate_ecommerce_value(ecommerce):
    """
    Calculate scoring value from ecommerce
    Can be 0 or 20
    """
    ec = 0
    if ecommerce:
        ec = 20
    return int(ec)

# Function to compute Affiliate Links
def calculate_affiliate_links_value(affiliate_links):
    """
    Calculate scoring value from affiliate_links
    Can be 0 or 10
    """
    al = 0
    if affiliate_links:
        al = 10
    return int(al)

# Function to compute Categories
def calculate_categories_value(categories_total):
    """
    Calculate scoring value from categories_total
    Can be 2, 4, 6, 8, 10
    """
    cat = 0
    if categories_total < 5:
        cat = 2
    elif 5 <= categories_total < 10:
        cat = 4
    elif 10 <= categories_total < 50:
        cat = 6
    elif 50 <= categories_total < 100:
        cat = 8
    elif categories_total >= 100:
        cat = 10
    return int(cat)

# Function to compute Total Categories
def count_categories_total(free_api_res):
    categories_total = 0
    for item in free_api_res["groups"]:
        for i in item["categories"]:
            categories_total += i["live"]
    return categories_total

# A function to compute BOR Score
def calculate_BOR_Score(data_pkg, validation=False):
    """
    Calculate BOR Score
    out of 100
    """
    weight = 100

    # each if else statement below adjusts the overall weighting for any missing values/empty fields
    # this can be adjusted in future, but is designed to not penailze a domain for empty or 0 values
    if data_pkg["sales_revenue"] == 0:
        sr = 0
        weight = weight - 20
    else:
        sr = calculate_sr_value(data_pkg["sales_revenue"])

    if data_pkg["mj_rank"] == 0:
        mj = 0
        weight = weight - 5
    else:
        mj = calculate_mj_value(data_pkg.get("mj_rank"))

    if data_pkg["mjtld_rank"] == 0:
        mjtld = 0
        weight = weight - 5
    else:
        mjtld = calculate_mjtld_value(data_pkg.get("mjtld_rank"))

    if data_pkg["ref_sn"] == 0:
        refsn = 0
        weight = weight - 5
    else:
        refsn = calculate_refsn_value(data_pkg.get("ref_sn"))

    if data_pkg["ref_ip"] == 0:
        refip = 0
        weight = weight - 5
    else:
        refip = calculate_refip_value(data_pkg.get("ref_ip"))

    # boolean values, no conditions
    po = calculate_payment_options_value(data_pkg.get("payment_options"))
    ec = calculate_ecommerce_value(data_pkg.get("ecommerce"))
    al = calculate_affiliate_links_value(data_pkg.get("affiliate_links"))

    if data_pkg["categories"] == 0:
        cat = 0
        weight = weight - 10
    else:
        cat = calculate_categories_value(data_pkg.get("categories"))

    sum = sr + mj + mjtld + refsn + refip + po + ec + al + cat
    score = round(sum / weight * 100)

    if validation:
        return int(score), weight, sum

    return int(score)

# a validation function to check the correctness of score
def validate_score(data_pkg):
    """
    Call this function to print all values in calculation
    For testing and error checking
    """
    print("----------")
    print("BOR SCORE VALIDATION")
    print("Data Dictionary input to BOR Score calculation:")
    print(data_pkg)
    print("")

    score, weight, sum = calculate_BOR_Score(data_pkg, validation=True)
    print("Final adjusted weight: ", weight)
    print(f"BOR Score will be calculated by {sum}/{weight} = {round(sum/weight, 5)}")
    print("")

    print("Calculated BOR Score: ", score)
    return


#########################
# Main                  #
#########################


def BOR(domain):
    # TO DO
    # implement error catching here
    # could run a check to see if domain exists in our master list, otherwise error
    # try except block added to get_json_from_bucket() could do this instead
    # check for vaild input
    hostname_bool = is_valid_domain(domain)

    # get search engine data from DataProvider
    if hostname_bool == False:
        print("Invalid domain provided!")
        return False
    else:
        print("Valid domain, calculating BOR Score...")

    domain_api_res = get_domain_api(domain)
    trust_api_res = get_trust_api(domain)
    free_api_res = get_free_api(domain)
    # parse json for data points
    # From BW Domain API Response
    sales_revenue = domain_api_res["Results"][0]["SalesRevenue"]
    # first_indexed = domain_api_res['Results'][0]['FirstIndexed']
    # years = years_since_first_indexed(first_indexed)
    mj_rank = domain_api_res["Results"][0]["Attributes"]["MJRank"]
    mjtld_rank = domain_api_res["Results"][0]["Attributes"]["MJTLDRank"]
    ref_sn = domain_api_res["Results"][0]["Attributes"]["RefSN"]
    ref_ip = domain_api_res["Results"][0]["Attributes"]["RefIP"]

    # From BW Trust API Response
    payment_options = trust_api_res["DBRecord"]["PaymentOptions"]
    ecommerce = trust_api_res["DBRecord"]["Ecommerce"]
    affiliate_links = trust_api_res["DBRecord"]["AffiliateLinks"]

    # From BW Free API Response
    categories_total = count_categories_total(free_api_res)

    # package data points
    data_pkg = {
        "sales_revenue": sales_revenue,
        "mj_rank": mj_rank,
        "mjtld_rank": mjtld_rank,
        "ref_sn": ref_sn,
        "ref_ip": ref_ip,
        "payment_options": payment_options,
        "ecommerce": ecommerce,
        "affiliate_links": affiliate_links,
        "categories": categories_total,
    }

    # calculate BOR Score
    bor = calculate_BOR_Score(data_pkg)

    calculation_version = "v0.1"

    # package results
    results_dict = {
        "hostname": domain,
        "BOR_Score": bor,
        "Version": calculation_version,
        "Timestamp": datetime.datetime.now().ctime(),
    }
    # update to store results package in document DB
    print(results_dict)

    # use to validate BOR Score calculation
    # validate_score(data_pkg)
