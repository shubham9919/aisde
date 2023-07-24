"""
This file is use to test database data, it includes insert data functions and delete data functions.
You can add/delete/update add in our database. 
"""


from common.database.sql_create_connection import cyber_db
from sqlalchemy.orm import Session
from common.database.sql_database_connection import CyberDatabase
# please remeber to add new sql models here
from common.database.sql_models import Base, ClientDataTable, ClientVendorsRelationshipTable, VendorDataTable, CompanyDataTable, TopCVETable, NVDDatabase, ResultTable, TrendResultTable, VendorRiskTable, PredictedWebsiteTable,  WebsiteTable, BundleAPITable,  DomainAPITable
from repository.sql_data_extraction_repo import CyberRepository
from common.database.sql_create_connection import cyber_db
from common.database.sql_models import Base
from common.database.database_connection import MongoDatabase

import random
import json
from sqlalchemy.orm.session import close_all_sessions

# must run it otherwises it will show not relation. It will create all the tables that defined in SQLAlchemy code, but not yet been created in the db.
Base.metadata.create_all(cyber_db.engine())


cyber_db = CyberDatabase()
cyber_repo = CyberRepository(cyber_db.engine(), cyber_db.metadata())
session = Session(cyber_db.engine())



def insert_client_data():
    """
    This function insert some data into client_data table.
    There is no specific input and output for this function because it basically insert data into client_data table. 
    client_id, client_name and client_domain are the attributes required to have value. By assign values to these attributes, it will add rows to specific table. Check Dbeaver to see exact data look like. 

    """

    for i in range(7):
        company_data =session.query(CompanyDataTable).filter(
                                CompanyDataTable.id == i). first()
                        

        if company_data is not None:
            client = ClientDataTable(client_id = company_data.id, client_name = company_data.company, 
                                                client_domain = company_data.hostname)


            session.add(client)

    session.commit()
    close_all_sessions()



def delete_client_data():
    """
    This function delete all data from client_data table..

    """
    session.query(ClientDataTable).delete()
    session.commit()





def generate_parent_child_company(d, parent=None):
    """
    Convert a nested dictionary into a list of dictionaries with the keys 'company_domain_id', 'parent_company_domain_id', and 'child_company_domain_id'.
    The nested dictionary can haev dynamic layer of dictionary. 
    
    Parameters:
    - d (dict): A nested dictionary representing a company hierarchy.
    - parent (str, optional): The name of the parent company. The default value is None.

    example of input: 
    - d (dict): {1: {   11: None,
        12: None}}
    - optional. parent_company_domain_id like 5 or None.
    
    Returns:
    - result (list): A list of dictionaries with the keys 'company_domain_id', 'parent_company_domain_id', and 'child_company_domain_id'.
    
    example of output:
    [{"company_domain_id": 1, "parent_company_domain_id": null, "child_company_domain_id": [11, 12]}, {"company_domain_id": 11, "parent_company_domain_id": 1, "child_company_domain_id": null}, {"company_domain_id": 12, "parent_company_domain_id": 1, "child_company_domain_id": null}]
    """


    # Initialize an empty list to store the resulting dictionaries
    result = []
    # Iterate through the key-value pairs in the input dictionary
    for k, v in d.items():
        # Create a new dictionary with the keys 'Company_name' and 'parent_company'
        item = {'company_domain_id': k, 'parent_company_domain_id': parent}
        # Check if the current value is a dictionary
        if isinstance(v, dict):
            # If the value is a dictionary, get a list of its keys
            child_companies = list(v.keys())
            # Set the 'child_company' key to the first key in the dictionary if it has only one key, or to a list of all the keys if it has more than one key 
            item['child_company_domain_id'] = child_companies[0] if len(child_companies) == 1 else child_companies
            # Add the current item to the result list    
            result.append(item)
            # Recursively call the generate_parent_child_companyt function on the dictionary with the current key as the parent
            result.extend(generate_parent_child_company(v, k))
        else:
            # If the value is not a dictionary, set the 'child_company' key to the value
            item['child_company_domain_id'] = v
            # Add the current item to the result list
            result.append(item)
    return result

def insert_enterpise_vendors_relationship_data():
    """
    This function insert some data into enterprise_vendors_relationship_data table.
    There is specific input and output. 
    The input has to be a list contains dictionary, the inside dictionary will be nested dictionary with dynamic layers.
    Example: 
        - [

    {1: {   11: None,
        12: None
    }
    }, 
    {2: {
        11: None, 
        12: None
    }}]
    Please check Dbeaver to see exact output data look like. It contains two attributes client_id, client_vendors_relationship for per row.
    """


    relationships = [

    {0: {   11: None,
        12: None
    }
    }, 
    {2: {
        11: None, 
        12: None
    }}, 
    {3:{
     11: {
        21: None
     }
    }
    }, 
    {4:{
        21: {
            11: None
        }
    }}, 
    {5:{
        11: None, 
        21: {
            22: {
                23: {
                    25: None
                }
            }, 
            24: {
                26: {
                    27: {
                        28: None
                    }
                }
            }
        }
    }}, 
    {6:{
        11: None, 
        21: {
            22: {
                23: {
                    25: None
                }
            }, 
            24: {
                26: {
                    27: {
                        28: None
                    }
                }
            }
        },
        29: {
          31: None, 
          32: {
            33: None
          }, 
          34: None
        }, 
        30: None
    }}
    ]
        
    for i in range(len(relationships)):
        k = list(relationships[i].keys())
        relation = generate_parent_child_company(relationships[i])
        session.add(ClientVendorsRelationshipTable(client_id = k[0], 
                                                client_vendors_relationship = relation))

    session.commit()
    close_all_sessions()


def delete_relationship_data():
    """
    This function delete all data from relationship_data table.

    """
    session.query(ClientVendorsRelationshipTable).delete()
    session.commit()


def insert_vendor_data():
    """
    This function insert some data into vendor_data table.
    There is no specific input and output for this function because it basically insert data into domain_data table. 
    vendor_domain_id, parent_client_id, f1, f2, f3 are the attributes required to have value. Be sure to map the data model requirement same as the ORM set up and data model defined.
    By assign values to these attributes, it will add rows to specific table. Check Dbeaver to see exact data look like.

    """
    relationships = session.query(ClientVendorsRelationshipTable).all()
    for i in relationships:
        relationship = i.client_vendors_relationship
        client_id = i.client_id
        for re in relationship:
            # transfer the result to integer.
            if re['parent_company_domain_id'] is not None:  
                vendor_domain_id = int(re['company_domain_id'])
                parent_client_id = client_id
                f1 = random.randint(0, 100)
                f2 = random.randint(0, 100)
                f3 = random.randint(0, 100)

                vendor = VendorDataTable(vendor_domain_id = vendor_domain_id, 
                                            parent_client_id = parent_client_id, 
                                            f1 = f1, f2 = f2, f3 = f3)

                session.add(vendor)

    session.commit()
    close_all_sessions()

def delete_vendor_data():
    """
    This function delete all data from vendor_data table.

    """
    session.query(VendorDataTable).delete()
    session.commit()


def mongo_db_company_db_data():
    """
    Function for migrate mongo db data into postgresql db.
    Please remember to create new SQL data model. 
    """
    # Connect to the MongoDB collection
    db = MongoDatabase().get_db()
    collection = db["Company_db"]

    # Get the documents from the collection
    mongo_docs = collection.find({})
    
    # Map the MongoDB documents to objects of the model class
    for doc in mongo_docs: 
        # print(doc)
        objs = CompanyDataTable(id = doc['ID'], company = doc['Company'],  hostname = doc['Hostname'])
        # print('obs', objs)
        # Add the objects to the session and commit the transaction
        session.add(objs)
    session.commit()
    # Close the session
    session.close()

def mongo_db_top_cve_db_data():
    """
    Function for migrate mongo db data into postgresql db.
    Please remember to create new SQL data model. 
    """
    # Connect to the MongoDB collection
    db = MongoDatabase().get_db()
    collection = db["Top_cve_data"]
    # Get the documents from the collection
    mongo_docs = collection.find({})
    # Map the MongoDB documents to objects of the model class
    for doc in mongo_docs: 
        objs = TopCVETable(CVE = doc['CVE'], technologies = doc['technologies'], impact = doc['Impact'], link = doc['link'], date = doc['date'])
        # Add the objects to the session and commit the transaction
        session.add(objs)
    session.commit()
    # Close the session
    session.close()



def mongo_db_nvd_data():
    """
    Function for migrate mongo db data into postgresql db.
    Please remember to create new SQL data model. 
    """
    # Connect to the MongoDB collection
    db = MongoDatabase().get_db()
    collection = db["NVD_Database"]

    # Get the documents from the collection
    mongo_docs = collection.find({})
    
    # Map the MongoDB documents to objects of the model class
    for doc in mongo_docs: 
        # if there is no scores, doc['scores'] will return an empty list.
        if isinstance(doc['scores'], list):
            objs = NVDDatabase(CVE = doc['CVE'], technologies = doc['technologies'], BaseScoreV2 = None, ExploitabilityScoreV2 = None, ImpactScoreV2 = None, BasescoreV3 = None, ExploitabilityScoreV3 = None, ImpactScoreV3 = None, Link = doc['link'])
            session.add(objs)
        # if there is any scores
        else:
            scores = doc['scores']
            BaseScoreV2 = scores.get("BaseScoreV2:", None)
            ExploitabilityScoreV2 = scores.get("ExploitabilityScoreV2", None)
            ImpactScoreV2 = scores.get("ImpactScoreV2", None)
            BasescoreV3 = scores.get("BasescoreV3", None)
            ExploitabilityScoreV3 = scores.get("ExploitabilityScoreV3", None)
            ImpactScoreV3 = scores.get("ImpactScoreV3", None)
            objs = NVDDatabase(CVE = doc['CVE'], technologies = doc['technologies'], BaseScoreV2 = BaseScoreV2, ExploitabilityScoreV2 = ExploitabilityScoreV2, ImpactScoreV2 = ImpactScoreV2, BasescoreV3 = BasescoreV3, ExploitabilityScoreV3 = ExploitabilityScoreV3, ImpactScoreV3 = ImpactScoreV3, Link = doc['link'])
            session.add(objs)
    session.commit()
    # Close the session
    session.close()


def mongo_db_result_data():

    """
    Function for migrate mongo db data into postgresql db.
    Please remember to create new SQL data model. 
    """
    # Connect to the MongoDB collection
    db = MongoDatabase().get_db()
    collection = db["Results_db"]
    # Get the documents from the collection
    mongo_docs = collection.find({})
    # Map the MongoDB documents to objects of the model class
    for doc in mongo_docs: 
        objs = ResultTable(id = doc['ID'], nvd_score = doc['nvd_score'], css_score = doc['css_score'], nvd_Date = doc['nvd_Date'], css_Date = doc['css_Date'], overall_score = doc['overall_score'], 
        overall_Date = doc['overall_Date'], breach_risk_score = doc['breach_risk_score'], breach_Date = doc['breach_Date'], bss_score = doc['bss_score'], bss_Date = doc['bss_score'], BSS = doc['BSS'])
        # Add the objects to the session and commit the transaction
        session.add(objs)
    session.commit()
    # Close the session
    session.close()



def mongo_db_trend_result_data():

    """
    Function for migrate mongo db data into postgresql db.
    Please remember to create new SQL data model. 
    """
    # Connect to the MongoDB collection
    db = MongoDatabase().get_db()
    collection = db["Trend_results_db"]
    # Get the documents from the collection
    mongo_docs = collection.find({})
    # Map the MongoDB documents to objects of the model class
    for doc in mongo_docs: 
        objs = TrendResultTable(id = doc['ID'], nvd_score = doc['nvd_score'], css_score = doc['css_score'], nvd_Date = doc['nvd_Date'], css_Date = doc['css_Date'], overall_score = doc['overall_score'], 
        overall_Date = doc['overall_Date'], breach_risk_score = doc['breach_risk_score'], breach_Date = doc['breach_Date'], bss_score = doc['bss_score'], bss_Date = doc['bss_score'], BSS = doc['BSS'])
        # Add the objects to the session and commit the transaction
        session.add(objs)
    session.commit()
    # Close the session
    session.close()


def mongo_db_vendor_risk_data():

    """
    Function for migrate mongo db data into postgresql db.
    Please remember to create new SQL data model. 
    """
    # Connect to the MongoDB collection
    db = MongoDatabase().get_db()
    collection = db["Vendor_risk_db"]
    # Get the documents from the collection
    mongo_docs = collection.find({})
    # Map the MongoDB documents to objects of the model class
    for doc in mongo_docs: 
        objs = VendorRiskTable(id = doc['ID'], Company = doc['Company'], Domain = doc['Domain'], Industry = doc['Industry'], Status = doc['Status'])
        # Add the objects to the session and commit the transaction
        session.add(objs)
    session.commit()
    # Close the session
    session.close()


def mongo_db_predict_website_data():

    """
    Function for migrate mongo db data into postgresql db.
    Please remember to create new SQL data model. 
    """
    # Connect to the MongoDB collection
    db = MongoDatabase().get_db()
    collection = db["predicted_website_db"]
    # Get the documents from the collection
    mongo_docs = collection.find({})
    # Map the MongoDB documents to objects of the model class
    for doc in mongo_docs: 


        features = doc['features']

        company = features['company']
        loadtime = features['loadtime']
        changes = features['changes']
        cloudscore = features['cloudscore']
        domainlength = features['domainlength']
        eii = features['eii']
        forwardingcount = features['forwardingcount']
        htmlsize = features['htmlsize']
        incominglinks = features['incominglinks']
        subdomainscount = features['subdomainscount']
        outgoinglinks = features['outgoinglinks']
        pagesindexed = features['pagesindexed']
        pages = features['pages']
        seo = features['seo']
        trustscore = features['trustscore']
        securityscore = features['securityscore']
        visitorsavg = features['visitorsavg']
        visitors = features['visitors']
        grade = features['grade']
        trustgrade = features['trustgrade']
        trafficindex = features['trafficindex']
        websiteage = features['websiteage']
        ecommercequality = features['ecommercequality']

        predictions = doc['predictions']

        probability = predictions['probability']
        Class = predictions['class'] 

        objs = PredictedWebsiteTable(date_executed = doc['date_executed'], hostname = doc['hostname'], 
        company = company, loadtime = loadtime, changes = changes, cloudscore = cloudscore, domainlength = domainlength, 
        eii = eii, forwardingcount = forwardingcount, htmlsize = htmlsize, incominglinks = incominglinks, subdomainscount = subdomainscount, 
        outgoinglinks = outgoinglinks, pagesindexed = pagesindexed, pages = pages, seo = seo, trustscore = trustscore, 
        securityscore = securityscore, visitorsavg = visitorsavg, visitors = visitors, grade = grade, trustgrade = trustgrade,
        trafficindex = trafficindex, websiteage = websiteage, ecommercequality = ecommercequality,
        probability = probability, Class = Class, success = doc['success'])
        # Add the objects to the session and commit the transaction
        session.add(objs)
    session.commit()
    # Close the session
    session.close()

def mongo_db_domain_api_data():
    with open('domain_api_db.json', 'r') as f: 
        data = json.load(f)
        row = DomainAPITable(domain_api_data = data)
        session.add(row)
    session.commit()
    session.close()


def mongo_db_bundle_api_data():
    with open('bundle_api_db.json', 'r') as f: 
        data = json.load(f)
        row = BundleAPITable(bundle_api_data = data)
        session.add(row)
    session.commit()
    session.close()


def mongo_db_website_data():
    with open('website_db.json', 'rb') as f: 
        data = f.read()
        decoded_data = data.decode('utf-8')
        row = WebsiteTable(website_data = decoded_data)
        session.add(row)
    session.commit()
    session.close()




def delete_all_data():
    """
    This function delete all data from four tables.

    """
    delete_client_data()
    delete_vendor_data()
    delete_relationship_data()

def insert_all_data():
    """
    This function insert some data into four tables.

    """
    mongo_db_company_db_data()
    insert_client_data()
    insert_enterpise_vendors_relationship_data()
    insert_vendor_data()
    mongo_db_nvd_data()    
    mongo_db_top_cve_db_data()
    # mongo_db_result_data()
    mongo_db_trend_result_data()
    mongo_db_vendor_risk_data()
    mongo_db_predict_website_data()
    mongo_db_domain_api_data()
    mongo_db_bundle_api_data()
    mongo_db_website_data()


insert_all_data()