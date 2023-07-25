"""
Fetch Data using SQLAlchemy queries
"""

import datetime
import json
import time
from datetime import timedelta
from typing import List
from flask import jsonify

import numpy as np
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Table, delete, func, select, bindparam, and_

from common.config_constants import (
    CLIENT_VENDORS_RELATIONSHIP_FOR_UI_TABLENAME,
    COMPANY_DOMAIN_DATA_TABLENAME,
    GENERAL_COMPANY_DATA_TABLENAME,
    RESULT_DATA_TABLENAME,
    SPECIFIC_COMPANY_DATA,
    VENDOR_AND_CLIENT_TABLENAME,
)
from sqlalchemy.orm import sessionmaker
from common.constant_database_variables import (
    OUTPUT_FEATURES_COLUMN_SPECIFIC_CLIENT,
    OUTPUT_RESULTS_COLUMN_SPECIFIC_CLIENT,
)

from common.database.sql_database_connection import CyberDatabase
from common.database.sql_models import (
    CompanyDomainDataTable,
    ResultTable,
    SpecificCompanyData,
    VendorAndClientTable,
)

Session = sessionmaker(bind=CyberDatabase().engine())
session = Session()


class ClientRepository(CyberDatabase):
    def get_general_client_data(self, company_id=None, company_name=None):
        output = []
        company_id = int(company_id) if company_id else None
        company_name = str(company_name).strip() if company_name else None

        if not company_id and not company_name:
            raise Exception(f"Please provide company name or ID!")

        try:
            with self.engine().begin() as connection:
                general_company_data_table = Table(
                    GENERAL_COMPANY_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                all_rows = None
                if company_id:
                    query = select([general_company_data_table]).where(
                        (general_company_data_table.c.company_id == company_id)
                    )
                    all_rows = connection.execute(query).fetchall()

                if company_name:
                    query = select([general_company_data_table]).where(
                        (general_company_data_table.c.company == company_name)
                    )
                    all_rows = connection.execute(query).fetchall()

                output = [dict(row) for row in all_rows] if all_rows else []
                return output

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def get_client_relationship_data(self, client_id):
        output = []
        client_id = int(client_id)
        try:
            with self.engine().begin() as connection:
                client_vendors_relationship_table = Table(
                    CLIENT_VENDORS_RELATIONSHIP_FOR_UI_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                query = select([client_vendors_relationship_table]).where(
                    (client_vendors_relationship_table.c.client_id == client_id)
                )

                all_rows = connection.execute(query).fetchall()
                output = [dict(row) for row in all_rows][0] if all_rows else []
                return output

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def get_self_client_score(self, client_id):
        output = []
        client_id = int(client_id)
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                result_table = Table(
                    RESULT_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                query = (
                    select(
                        [
                            result_table.c[column_name]
                            for column_name in OUTPUT_RESULTS_COLUMN_SPECIFIC_CLIENT
                        ]
                    )
                    .select_from(
                        result_table.join(
                            vendor_and_parent_table,
                            result_table.c.vendor_client_row_id
                            == vendor_and_parent_table.c.vendor_client_row_id,
                        )
                    )
                    .where(
                        and_(
                            vendor_and_parent_table.c.client_id == client_id,
                            vendor_and_parent_table.c.vendor_id == None,
                        )
                    )
                    .order_by(result_table.c.datetime_executed.desc())
                    .limit(1)
                )

                all_rows = connection.execute(query).fetchall()
                output = [dict(row) for row in all_rows] if all_rows else []
                print(output)
                return output

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def get_vendor_score(self, client_id, vendor_list: List):
        output = []
        vendor_list = [name.lower() for name in vendor_list]
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                result_table = Table(
                    RESULT_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                all_domains_table = Table(
                    COMPANY_DOMAIN_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                # Verify If all Vendors Exist

                get_all_vendor_ids_query = select(
                    [
                        all_domains_table.c["company_id"],
                        func.lower(all_domains_table.c["company_name"]).label(
                            "company_name"
                        ),
                        func.lower(all_domains_table.c["domain_name"]).label(
                            "domain_name"
                        ),
                    ]
                ).where(
                    and_(
                        all_domains_table.c.domain_name.in_(vendor_list),
                    )
                )

                all_available_domains = connection.execute(
                    get_all_vendor_ids_query
                ).fetchall()

                print(all_available_domains)
                all_available_domains_dict_list = (
                    [dict(row) for row in all_available_domains]
                    if all_available_domains
                    else []
                )

                all_available_domains_with_ids = [
                    dict_obj["company_id"]
                    for dict_obj in all_available_domains_dict_list
                ]
                print(all_available_domains_with_ids)

                get_client_vendor_row_id_query = (
                    select(
                        [
                            result_table.c[column_name]
                            for column_name in OUTPUT_RESULTS_COLUMN_SPECIFIC_CLIENT
                        ]
                        + [
                            all_domains_table.c["company_name"],
                            all_domains_table.c["domain_name"],
                        ]
                    )
                    .select_from(
                        result_table.join(
                            vendor_and_parent_table,
                            result_table.c.vendor_client_row_id
                            == vendor_and_parent_table.c.vendor_client_row_id,
                        ).join(
                            all_domains_table,
                            vendor_and_parent_table.c.vendor_id
                            == all_domains_table.c.company_id,
                        )
                    )
                    .where(
                        and_(
                            vendor_and_parent_table.c.client_id == client_id,
                            vendor_and_parent_table.c.vendor_id.in_(
                                all_available_domains_with_ids
                            ),
                        )
                    )
                    .order_by(result_table.c.datetime_executed.desc())
                    .limit(1)
                )

                all_results = connection.execute(
                    get_client_vendor_row_id_query
                ).fetchall()

                all_results_dict_list = (
                    [dict(row) for row in all_results] if all_results else []
                )

                return all_results_dict_list

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def get_all_vendor_score(self, client_id):
        output = []
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                result_table = Table(
                    RESULT_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                all_domains_table = Table(
                    COMPANY_DOMAIN_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                get_client_vendor_row_id_query = (
                    select(
                        [
                            result_table.c[column_name]
                            for column_name in OUTPUT_RESULTS_COLUMN_SPECIFIC_CLIENT
                        ]
                        + [
                            all_domains_table.c["company_name"],
                            all_domains_table.c["domain_name"],
                        ]
                    )
                    .select_from(
                        result_table.join(
                            vendor_and_parent_table,
                            result_table.c.vendor_client_row_id
                            == vendor_and_parent_table.c.vendor_client_row_id,
                        ).join(
                            all_domains_table,
                            vendor_and_parent_table.c.vendor_id
                            == all_domains_table.c.company_id,
                        )
                    )
                    .where(
                        and_(
                            vendor_and_parent_table.c.client_id == client_id,
                        )
                    )
                    .order_by(result_table.c.datetime_executed.desc())
                    .limit(1)
                )

                all_results = connection.execute(
                    get_client_vendor_row_id_query
                ).fetchall()

                all_results_dict_list = (
                    [dict(row) for row in all_results] if all_results else []
                )

                return all_results_dict_list

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def get_self_client_features(self, client_id):
        output = []
        client_id = int(client_id)
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                specific_company_data_table = Table(
                    SPECIFIC_COMPANY_DATA,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                query = (
                    select(
                        [
                            specific_company_data_table.c[column_name]
                            for column_name in OUTPUT_FEATURES_COLUMN_SPECIFIC_CLIENT
                        ]
                    )
                    .select_from(
                        specific_company_data_table.join(
                            vendor_and_parent_table,
                            specific_company_data_table.c.vendor_client_row_id
                            == vendor_and_parent_table.c.vendor_client_row_id,
                        )
                    )
                    .where(
                        and_(
                            vendor_and_parent_table.c.client_id == client_id,
                            vendor_and_parent_table.c.vendor_id == None,
                        ),
                    )
                )

                all_rows = connection.execute(query).fetchall()
                output = [dict(row) for row in all_rows][0] if all_rows else []
                return output

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def get_vendor_features(self, client_id, vendor_list: List):
        vendor_list = [name.lower() for name in vendor_list]
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                specific_company_data_table = Table(
                    SPECIFIC_COMPANY_DATA,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                all_domains_table = Table(
                    COMPANY_DOMAIN_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                # Verify If all Vendors Exist

                get_all_vendor_ids_query = select(
                    [
                        all_domains_table.c["company_id"],
                        func.lower(all_domains_table.c["company_name"]).label(
                            "company_name"
                        ),
                        func.lower(all_domains_table.c["domain_name"]).label(
                            "domain_name"
                        ),
                    ]
                ).where(
                    and_(
                        all_domains_table.c.domain_name.in_(vendor_list),
                    )
                )

                all_available_domains = connection.execute(
                    get_all_vendor_ids_query
                ).fetchall()

                all_available_domains_dict_list = (
                    [dict(row) for row in all_available_domains]
                    if all_available_domains
                    else []
                )

                all_available_domains_with_ids = [
                    dict_obj["company_id"]
                    for dict_obj in all_available_domains_dict_list
                ]

                get_client_vendor_row_id_query = (
                    select(
                        [
                            specific_company_data_table.c[column_name]
                            for column_name in OUTPUT_FEATURES_COLUMN_SPECIFIC_CLIENT
                        ]
                        + [
                            all_domains_table.c["company_name"],
                            all_domains_table.c["domain_name"],
                        ]
                    )
                    .select_from(
                        specific_company_data_table.join(
                            vendor_and_parent_table,
                            specific_company_data_table.c.vendor_client_row_id
                            == vendor_and_parent_table.c.vendor_client_row_id,
                        ).join(
                            all_domains_table,
                            vendor_and_parent_table.c.vendor_id
                            == all_domains_table.c.company_id,
                        )
                    )
                    .where(
                        and_(
                            vendor_and_parent_table.c.client_id == client_id,
                            vendor_and_parent_table.c.vendor_id.in_(
                                all_available_domains_with_ids
                            ),
                        )
                    )
                )

                all_results = connection.execute(
                    get_client_vendor_row_id_query
                ).fetchall()

                all_results_dict_list = (
                    [dict(row) for row in all_results] if all_results else []
                )

                return all_results_dict_list

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def get_all_vendor_features(self, client_id):
        output = []
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                specific_company_data_table = Table(
                    SPECIFIC_COMPANY_DATA,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                all_domains_table = Table(
                    COMPANY_DOMAIN_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                get_client_vendor_row_id_query = (
                    select(
                        [
                            specific_company_data_table.c[column_name]
                            for column_name in OUTPUT_FEATURES_COLUMN_SPECIFIC_CLIENT
                        ]
                        + [
                            all_domains_table.c["company_name"],
                            all_domains_table.c["domain_name"],
                        ]
                    )
                    .select_from(
                        specific_company_data_table.join(
                            vendor_and_parent_table,
                            specific_company_data_table.c.vendor_client_row_id
                            == vendor_and_parent_table.c.vendor_client_row_id,
                        ).join(
                            all_domains_table,
                            vendor_and_parent_table.c.vendor_id
                            == all_domains_table.c.company_id,
                        )
                    )
                    .where(
                        and_(
                            vendor_and_parent_table.c.client_id == client_id,
                        )
                    )
                )

                all_results = connection.execute(
                    get_client_vendor_row_id_query
                ).fetchall()

                all_results_dict_list = (
                    [dict(row) for row in all_results] if all_results else []
                )

                return all_results_dict_list

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def delete_vendors(self, client_id, vendor_list: List):
        vendor_list = [name.lower() for name in vendor_list]
        print("here")
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                all_domains_table = Table(
                    COMPANY_DOMAIN_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                # Verify If all Vendors Exist

                get_all_vendor_ids_query = select(
                    [
                        all_domains_table.c["company_id"],
                        func.lower(all_domains_table.c["company_name"]).label(
                            "company_name"
                        ),
                        func.lower(all_domains_table.c["domain_name"]).label(
                            "domain_name"
                        ),
                    ]
                ).where(
                    and_(
                        all_domains_table.c.domain_name.in_(vendor_list),
                    )
                )

                all_available_domains = connection.execute(
                    get_all_vendor_ids_query
                ).fetchall()

                all_available_domains_dict_list = (
                    [dict(row) for row in all_available_domains]
                    if all_available_domains
                    else []
                )

                all_available_domains_with_ids = [
                    dict_obj["company_id"]
                    for dict_obj in all_available_domains_dict_list
                ]

                all_available_domains_with_name = [
                    (dict_obj["company_name"], dict_obj["domain_name"])
                    for dict_obj in all_available_domains_dict_list
                ]

                get_client_vendor_row_id_query = delete(vendor_and_parent_table).where(
                    and_(
                        vendor_and_parent_table.c.client_id == client_id,
                        vendor_and_parent_table.c.vendor_id.in_(
                            all_available_domains_with_ids
                        ),
                    )
                )

                all_results = connection.execute(get_client_vendor_row_id_query)

                return all_available_domains_with_name

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def delete_all_vendors(self, client_id):
        try:

            with self.engine().begin() as connection:
                vendor_and_parent_table = Table(
                    VENDOR_AND_CLIENT_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                all_domains_table = Table(
                    COMPANY_DOMAIN_DATA_TABLENAME,
                    self.metadata(),
                    autoload=True,
                    autoload_with=connection,
                )

                # Verify If all Vendors Exist

                get_all_vendor_ids_query = (
                    select(
                        [
                            all_domains_table.c["company_id"],
                            func.lower(all_domains_table.c["company_name"]).label(
                                "company_name"
                            ),
                            func.lower(all_domains_table.c["domain_name"]).label(
                                "domain_name"
                            ),
                        ]
                    )
                    .select_from(
                        all_domains_table.join(
                            vendor_and_parent_table,
                            vendor_and_parent_table.c.vendor_id
                            == all_domains_table.c.company_id,
                        )
                    )
                    .where(and_(vendor_and_parent_table.c.client_id == client_id))
                )

                all_available_domains = connection.execute(
                    get_all_vendor_ids_query
                ).fetchall()

                all_available_domains_dict_list = (
                    [dict(row) for row in all_available_domains]
                    if all_available_domains
                    else []
                )

                all_deleted_vendors = [
                    (dict_obj["company_name"], dict_obj["domain_name"])
                    for dict_obj in all_available_domains_dict_list
                ]

                delete_all_vendors_query = delete(vendor_and_parent_table).where(
                    and_(vendor_and_parent_table.c.client_id == client_id)
                )

                all_results = connection.execute(delete_all_vendors_query)

                return all_deleted_vendors

        except Exception as err:
            raise Exception(
                f"{str(err)} Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA"
            )

    def post_direct_client_technologies(self, client_id, path_to_csv):

        df = pd.read_csv(path_to_csv)
        df = df.rename(columns={"company": "company_name", "domain": "domain_name"})

        all_vendor_domains_with_name = df[["company_name", "domain_name"]].to_dict(
            orient="records"
        )

        all_company_ids_with_domain = (
            self.insert_into_company_domain_table_with_domain_and_names(
                all_vendor_domains_with_name
            )
        )

        all_vendor_ids = all_company_ids_with_domain["company_id"].to_list() + [None]
        all_parent_vendor_row_id_with_domain_id = self.insert_into_vendor_parent_table(
            client_id, all_vendor_ids
        )
        domains_with_id_and_technologies = df.merge(
            all_company_ids_with_domain, on=["company_name", "domain_name"]
        )

        df_with_all_data = domains_with_id_and_technologies.merge(
            all_parent_vendor_row_id_with_domain_id,
            left_on="company_id",
            right_on="vendor_id",
        )

        self.insert_into_vendor_client_technologies_table(df_with_all_data)

        return jsonify({"message": "Data inserted!"})

    def post_enterprise_vendor_technologies(self, client_id, path_to_csv):

        df = pd.read_csv(path_to_csv)
        df = df.rename(
            columns={"vendor": "company_name", "vendor_domain": "domain_name"}
        )
        all_vendor_domains_with_name = df[["company_name", "domain_name"]].to_dict(
            orient="records"
        )

        all_company_ids_with_domain = (
            self.insert_into_company_domain_table_with_domain_and_names(
                all_vendor_domains_with_name
            )
        )

        all_vendor_ids = all_company_ids_with_domain["company_id"].to_list() + [None]

        all_parent_vendor_row_id_with_domain_id = self.insert_into_vendor_parent_table(
            client_id, all_vendor_ids
        )
        domains_with_id_and_technologies = df.merge(
            all_company_ids_with_domain, on=["company_name", "domain_name"]
        )

        df_with_all_data = domains_with_id_and_technologies.merge(
            all_parent_vendor_row_id_with_domain_id,
            left_on="company_id",
            right_on="vendor_id",
        )

        self.insert_into_vendor_client_technologies_table(df_with_all_data)

        return jsonify({"message": "Data inserted!"})

    def insert_into_company_domain_table_with_domain_and_names(
        self, all_vendor_domains_with_name
    ):
        with self.engine().begin() as connection:
            query = insert(CompanyDomainDataTable).values(all_vendor_domains_with_name)
            query = query.on_conflict_do_update(
                index_elements=[
                    CompanyDomainDataTable.company_name,
                    CompanyDomainDataTable.domain_name,
                ],
                set_={
                    "company_name": query.excluded.company_name,
                    "domain_name": query.excluded.domain_name,
                },
            ).returning(
                CompanyDomainDataTable.company_id,
                CompanyDomainDataTable.company_name,
                CompanyDomainDataTable.domain_name,
            )

            all_domain_ids = connection.execute(query).fetchall()
            session.commit()    

            df = pd.DataFrame(
                data=all_domain_ids,
                columns=["company_id", "company_name", "domain_name"],
            )

        return df

    def insert_into_vendor_parent_table(self, client_id, domain_id_list):

        rows_formatted_input = [
            {"vendor_id": vendor_domain_id, "client_id": client_id}
            for vendor_domain_id in domain_id_list
        ]

        with self.engine().begin() as connection:
            query = insert(VendorAndClientTable).values(rows_formatted_input)

            query = query.on_conflict_do_update(
                index_elements=[
                    VendorAndClientTable.vendor_id,
                    VendorAndClientTable.client_id,
                ],
                set_={
                    "vendor_id": query.excluded.vendor_id,
                    "client_id": query.excluded.client_id,
                },
            ).returning(
                VendorAndClientTable.vendor_client_row_id,
                VendorAndClientTable.vendor_id,
                VendorAndClientTable.client_id,
            )

            all_records = connection.execute(query).fetchall()
            session.commit()

            df = pd.DataFrame(
                data=all_records,
                columns=[
                    "vendor_client_row_id",
                    "vendor_id",
                    "client_id",
                ],
            )

        return df

    def insert_into_vendor_client_technologies_table(
        self, df_with_parent_vendor_row_id_and_technologies
    ):

        df_with_parent_vendor_row_id_and_technologies[
            "technologies"
        ] = df_with_parent_vendor_row_id_and_technologies["technologies"].apply(
            lambda x: set(word.strip() for word in str(x).split(",")) if x else [None]
        )

        rows_formatted_input = df_with_parent_vendor_row_id_and_technologies[
            ["vendor_client_row_id", "technologies"]
        ].to_dict(orient="records")

        with self.engine().begin() as connection:
            query = insert(SpecificCompanyData).values(rows_formatted_input)

            query = query.on_conflict_do_update(
                index_elements=[
                    SpecificCompanyData.vendor_client_row_id,
                ],
                set_={
                    "vendor_client_row_id": query.excluded.vendor_client_row_id,
                    "technologies": query.excluded.technologies,
                },
            )

            connection.execute(query)
