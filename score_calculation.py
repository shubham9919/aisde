"""
This file is use to calculate scores for each client.
"""


import datetime
import time
from datetime import timedelta
from common.database.sql_create_connection import cyber_repo, cyber_db
from sqlalchemy.orm import Session
from sqlalchemy import Table, and_, bindparam, select, MetaData, Column, Integer, String

from common.database.sql_database_connection import CyberDatabase
from common.database.sql_models import Base, ClientDataTable, DomainDataTable, ClientVendorsRelationshipTable, VendorDataTable
from repository.sql_data_extraction_repo import CyberRepository



from common.database.sql_create_connection import cyber_db
from common.database.sql_models import Base

# must run it otherwises it will show not relation. It will create all the tables that defined in SQLAlchemy code, but not yet been created in the db.
Base.metadata.create_all(cyber_db.engine())


cyber_db = CyberDatabase()
cyber_repo = CyberRepository(cyber_db.engine(), cyber_db.metadata())
session = Session(cyber_db.engine())



def create_parent_list(relationships):
    """
    This function is used to create parent list that contains multiple dictionary. Inside dictionary contains root parent id and its child id.
    Input: 
        - relationships: list of common.database.sql_models.ClientVendorsRelationshipTable object
    Output:
        - parent_list: list of dictionary. 
            - sample output: [{'root_parent_id': 1, 'child_id': [11, 12]}, {'root_parent_id': 2, 'child_id': [11, 12]}, {'root_parent_id': 3, 'child_id': 11}, {'root_parent_id': 4, 'child_id': 21}, {'root_parent_id': 5, 'child_id': [11, 21]}]
    """

    parent_list = []
    for m in relationships:
        for relationship in m.client_vendors_relationship:
            if relationship['company_domain_id'] == m.client_id:
                parent_list.append({'root_parent_id':m.client_id, 'child_id':relationship['child_company_domain_id']})
    return parent_list


def get_vendor_sum_scores(db: Session, vendor_domain_id: int, parent_client_id: int):
    """
    This function is used to get vendor's data for given vendor_domain_id and parent_client_id.
    Input: 
        - db: SQLAchemy connect session
        - vendor_domain_id: integer
        - parent_client_id: integer
    Output:
        - vendor_data: common.database.sql_models.VendorDataTable object. 
    """

    # Query the VendorDataTable to get the f1, f2, and f3 values for this company
    vendor_data = (
                    db.query(
                        VendorDataTable.f1,
                        VendorDataTable.f2,
                        VendorDataTable.f3,
                    )
                    .filter(
                        VendorDataTable.vendor_domain_id == vendor_domain_id,
                        VendorDataTable.parent_client_id == parent_client_id,
                    )
                    .first()
                )

    return vendor_data



def calculate_total_scores(db: Session, client_id: int, company_domain_id: int) -> int:
    """
    This function is used to calculate total children company f1+f2+f3 scores for given company_domain_id and the client_id
    Input: 
        - db: SQLAchemy connect session
        - client: integer
        - company_domain_id: integer
    Output:
        - total_score: int 
    Sample usage:
        calculate_total_scores(session, client_id=5, company_domain_id=24)
    """

    # Query the ClientVendorsRelationshipTable to get the client_vendors_relationship column
    # for the given client_id
    client_vendors_relationship = (
        db.query(ClientVendorsRelationshipTable.client_vendors_relationship)
        .filter(ClientVendorsRelationshipTable.client_id == client_id)
        .first()
    )
    
    # If the client_vendors_relationship is None or empty, then return 0
    if client_vendors_relationship is None or not client_vendors_relationship:
        return 0
    
    # Get the list of dictionaries from the client_vendors_relationship tuple
    client_vendors_relationship = client_vendors_relationship[0]
    
    # Initialize a variable to store the total score
    total_score = 0
    
    # Iterate over each company in the client_vendors_relationship
    for company in client_vendors_relationship:
        # If the company has a parent_company_domain_id, then this company is a child company
        if company['parent_company_domain_id'] is not None:
            # If the parent_company_domain_id of this company matches the given company_domain_id,
            # then this company is a child of the given company
            if company['parent_company_domain_id'] == company_domain_id:
                # Query the VendorDataTable to get the f1, f2, and f3 values for this company
                # Add the f1, f2, and f3 values to the total score
                vendor_data = get_vendor_sum_scores(session, company['company_domain_id'], client_id)
                total_score += vendor_data.f1 + vendor_data.f2 + vendor_data.f3
            
                # If the company has child_company_domain_ids,
                # then recursively call the function to add the total scores for the children of this company
                if company['child_company_domain_id'] is not None:
                    total_score += calculate_total_scores(db, client_id, company['company_domain_id'])
    
    # Return the total score
    return total_score


def calculate_sum_score(vendors, relationships, session): 
    """
    This function is used to calculate the final sum score for every client with its given relationship.
    Input: 
        - vendors: list of common.database.sql_models.VendorDataTable object. 
        - relationship: list of common.database.sql_models.ClientVendorsRelationshipTable object. 
        - session: SQLAchemy connect session
    Output:
        - result_list: list of dictionary. It contains score result for each client. 
            - sample output: [{'client_id': 1, 'final_score': 1143}, {'client_id': 2, 'final_score': 624}, {'client_id': 3, 'final_score': 32256.0}, {'client_id': 4, 'final_score': 14274.666666666668}, {'client_id': 5, 'final_score': 242895.6666666667}]
    Sample usage:
        calculate_sum_score(vendors, relationships, session)
    """

    # get the parent list
    parent_list = create_parent_list(relationships)
    # initial result list and final score
    result_list = []
    final_score = 0 

    # i is the parent child dictionary
    for i in parent_list:
        # if there are over 1 child in the relationship
        if isinstance(i['child_id'], list): 
            for child in i['child_id']:
                child_score = calculate_total_scores(session, client_id=i['root_parent_id'], company_domain_id= child)
                # get vendor data for this specific company, f1, f2 and f3 score.
                vendor_data = get_vendor_sum_scores(session, child, i['root_parent_id'])

                # Add the f1, f2, and f3 values to the total score                
                # final_score += child_score / 3 * (2 * vendor_data.f1 + 3*vendor_data.f2 + 4*vendor_data.f3)
                if child_score == 0: 
                    final_score += 2 * vendor_data.f1 + 3*vendor_data.f2 + 4*vendor_data.f3
                else:
                    final_score += child_score / 3 * (2 * vendor_data.f1 + 3*vendor_data.f2 + 4*vendor_data.f3)
                # print(final_score)
        else:
            # get vendor data
            vendor_data = get_vendor_sum_scores(session, i['child_id'], i['root_parent_id'])
            # get child sum scores
            child_score = calculate_total_scores(session, client_id=i['root_parent_id'], company_domain_id= i['child_id'])

            # if the client only has one child company
            if child_score == 0: 
                final_score += 2 * vendor_data.f1 + 3*vendor_data.f2 + 4*vendor_data.f3
            else:
                final_score += child_score / 3 * (2 * vendor_data.f1 + 3*vendor_data.f2 + 4*vendor_data.f3)


        # add final score result to result list
        result_list.append({'client_id': i['root_parent_id'], 'final_score': final_score})
        # return to 0 and it will calcualte score for next root_parent_id
        final_score = 0     

    return result_list

# get data from vendor data table.
vendors = session.query(VendorDataTable).all()
# get data from client vendors relationship tabl. 
relationships = session.query(ClientVendorsRelationshipTable).all()
# calculate total sum score for client
print(calculate_sum_score(vendors, relationships, session))
