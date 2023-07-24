""""
This file is used to test if data input from HTML can be insert into ClientVendorRelationshipTable.
It first parse HTML content into dictionary, and then convert into form of list of dictionary. e.g # [{'Amazon': {'Google': None, 'B': 'm', 'C' : {'D': 'n', 'E': None}}}, {'Alex': None}]
The final data store in ClientVendorRelationshipTable require to follow the data model defination and restrictions. Check common\sql_models.py for more information. 

There is another method to hard input relationship data and it is in submit_test.py file. 
The hard input data sample: input = {
    'Amazon': {
        'Google': None,
        'B': 1,
        'C': {
            'D': {
                'F': '3',
                'G': {'H' : {
                    'J': {'K': 'L'}
                }}
            },
            'E': None
        }
    }
}
"""


# pip install BeautifulSoup4
from bs4 import BeautifulSoup
import datetime
import time
from datetime import timedelta
from common.database.sql_create_connection import cyber_repo, cyber_db
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from sqlalchemy import Table, and_, bindparam, select

from common.database.sql_database_connection import CyberDatabase
from common.database.sql_models import Base, ClientDataTable, ClientVendorsRelationshipTable, VendorDataTable
from repository.sql_data_extraction_repo import CyberRepository

from common.database.sql_create_connection import cyber_db
from common.database.sql_models import Base

Base.metadata.create_all(cyber_db.engine())

cyber_db = CyberDatabase()
cyber_repo = CyberRepository(cyber_db.engine(), cyber_db.metadata())
session = Session(cyber_db.engine())


# sample html input body. It can change value in <li>.
htmlbody = '''
    <ol>
      <li> 5
        <ol>
          <li>
            11
          </li>
          <li>
            21
                <ol>
                <li>
                22
                    <ol>
                    <li>
                    23
                        <ol>
                        <li>
                        25
                        </li>
                        </ol>
                    </li>
                    </ol>
                </li>
                <li>
                24
                    <ol>
                    <li>
                    26
                        <ol>
                        <li>
                        27
                            <ol>
                            <li>
                            28
                            </li>
                            </ol>
                        </li>
                        </ol>
                    </li>
                    </ol>
                </li>
                </ol>
          </li>
        </ol>
      </li>
    </ol>

'''


def ol_to_dict(ol):
    """
    This function is used to convert order list HTML element into dictionary
    Input: 
        - ol: parsed HTML order list element. 
    Output:
        - result: dictionary. It contains score result for each client. 
            - sample output: {'5': {'11': None, '21': {'22': {'23': {'25': None}}, '24': {'26': {'27': {'28': None}}}}}}      
    """
    list_of_dict = []
    result = {}
    for li in ol.find_all("li", recursive=False):
        key = next(li.stripped_strings)
        ol = li.find("ol")
        if ol:
            result[key] = ol_to_dict(ol)
        else:
            result[key] = None
    return result

def convert_dictionary_to_list_dictionary(dict_result):
    """
    This function is used to convert dictionary output from function ol_to_dict(ol) to list of dictionary form.
    Input: 
        - dict_result: dictionary form of parsed HTML order list element. 
    Output:
        - list_result: dictionary. It contains score result for each client. 
            - sample output: [{'5': {'11': None, '21': {'22': {'23': {'25': None}}, '24': {'26': {'27': {'28': None}}}}}}]    
        - list_client_id: ['5', '21']
    """
    list_client_id = []
    list_result = []
    new_dict = {}
    for key, value in dict_result.items():
        new_dict[key] = value
        list_result.append(new_dict)
        list_client_id.append(key)
        new_dict = {}
    return list_result, list_client_id


# Let BeautifulSoup do it's magic and parse ul from the HTML.
htmlbody = BeautifulSoup(htmlbody, features="html.parser").ol
dict_relationship = ol_to_dict(htmlbody)
relationships,  list_client_id= convert_dictionary_to_list_dictionary(dict_relationship)
print(list_client_id)


def generate_parent_child_company(d, parent=None):
    """
    Convert a nested dictionary into a list of dictionaries with the keys 'Company_name', 'parent_company', and 'child_company'.
    The nested dictionary can haev dynamic layer of dictionary. 
    
    Parameters:
    - d (dict): A nested dictionary representing a company hierarchy.
    - parent (str, optional): The name of the parent company. The default value is None.
    
    Returns:
    - result (list): A list of dictionaries with the keys 'Company_name', 'parent_company', and 'child_company'.
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


def insert_client_vendors_relationship_data():
    """
    This function insert some data into enterprise_vendors_relationship_data table.
    There is specific input and output. 
    The input has to be a list contains dictionary, the inside dictionary will be nested dictionary with dynamic layers.
    """
        
    for i in range(len(relationships)):
        relation = generate_parent_child_company(relationships[i])
        session.add(ClientVendorsRelationshipTable(client_id = list_client_id[i], 
                                                client_vendors_relationship = relation))


    session.commit()
    session.close_all()


def delete_relationship_data():
    """
    This function delete all data from ClientVendorsRelationshipTable.

    """
    session.query(ClientVendorsRelationshipTable).delete()
    session.commit()

insert_client_vendors_relationship_data()
# delete_relationship_data()