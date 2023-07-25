import datetime
import time
from datetime import timedelta
from common.database.sql_create_connection import cyber_repo, cyber_db
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from sqlalchemy import Table, and_, bindparam, select

from common.database.sql_database_connection import CyberDatabase
from common.database.sql_models import Base, CompanyDataTable, CompanyEnterpriseDataTable, EnterpriseVendorsRelationshipTable
from repository.sql_data_extraction_repo import CyberRepository

cyber_db = CyberDatabase()
cyber_repo = CyberRepository(cyber_db.engine(), cyber_db.metadata())
session = Session(cyber_db.engine())



def insert_enterpise_data():
    # delete_all_data()
    enterprise_domain_list = []
    company_data_list = []

    for i in range(10):
        company_name = f'Enterprise{i}'
        domain_name = f'www.domain{i}.com'

        enterprise = CompanyEnterpriseDataTable(company_name = company_name, 
                                                company_domain = domain_name)
        enterprise_domain_list.append(enterprise)

        

    session.add_all(enterprise_domain_list)
    session.commit()

    for i in range(10):
        company_name = f'Enterprise{i}'
        domain_name = f'www.domain{i}.com'

        result = session.query(CompanyEnterpriseDataTable).filter(CompanyEnterpriseDataTable.company_domain == domain_name)
        parent_enterprise = result[0].company_enterprise_id

        company_data = CompanyDataTable(company_name = company_name,
                                        domain = domain_name,
                                        parent_enterprise=parent_enterprise,
                                        f1=10,
                                        f2=20,
                                        f3=60)
        
        company_data_list.append(company_data)


        if parent_enterprise %3 == 0:
            vendor_name = f'Vendor{i}'
            vendor_domain = f'www.vendor_domain{i}.com'

            vendor_data = CompanyDataTable(company_name = vendor_name,
                                    domain = vendor_domain,
                                    parent_enterprise=parent_enterprise,
                                    f1=10,
                                    f2=20,
                                    f3=60)

        
            company_data_list.append(vendor_data)

    session.add_all(company_data_list)
    session.commit()
    session.close_all()
                                

def insert_companmy_data():
    company_data_list = []
    for i in range(10):
        pass
        


def delete_enterprise_data():
    session.query(CompanyEnterpriseDataTable).delete()
    session.commit()

def delete_relationship_data():
    session.query(EnterpriseVendorsRelationshipTable).delete()
    session.commit()

def delete_vendor_data():
    session.query(CompanyDataTable).delete()
    session.commit()

def delete_all_data():
    delete_enterprise_data()
    delete_relationship_data()
    delete_vendor_data()

insert_enterpise_data()