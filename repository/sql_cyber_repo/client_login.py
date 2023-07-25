"""
Fetch Data using SQLAlchemy queries
"""

import datetime
import json
import time
from datetime import timedelta
from flask import jsonify
from flask_jwt_extended import create_access_token

import numpy as np
import pandas as pd
from sqlalchemy import Table, select, bindparam, and_
from common.config_constants import (
    CLIENT_VENDORS_RELATIONSHIP_FOR_UI_TABLENAME,
    GENERAL_COMPANY_DATA_TABLENAME,
)
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt

from common.database.sql_database_connection import CyberDatabase
from common.database.sql_models import (
    ClientLoginTable,
    CompanyDomainDataTable,
    RegisteredClientDataTable,
)

Session = sessionmaker(bind=CyberDatabase().engine())
session = Session()


def generate_token(email_id, client_id):
    identity = {"email_id": email_id, "client_id": client_id}
    return create_access_token(identity=identity)


class ClientLoginRepository(CyberDatabase):
    def registration(self, client_name, domain_name, email_id, hashed_password):

        try:
            is_client_and_domain_registered = (
                session.query(RegisteredClientDataTable.client_id)
                .filter(
                    and_(
                        RegisteredClientDataTable.client_domain == domain_name,
                        RegisteredClientDataTable.client_name == client_name,
                    )
                )
                .first()
            )

            client_id = (
                is_client_and_domain_registered[0]
                if is_client_and_domain_registered
                else None
            )

            is_name_and_domain_in_all_company_table = (
                session.query(CompanyDomainDataTable)
                .filter(
                    and_(
                        CompanyDomainDataTable.domain_name == domain_name,
                        CompanyDomainDataTable.company_name == client_name,
                    )
                )
                .first()
            )

            if not is_name_and_domain_in_all_company_table:
                store_client_domain_in_all_company_table = CompanyDomainDataTable(
                    company_name=client_name, domain_name=domain_name
                )
                session.add(store_client_domain_in_all_company_table)
                session.commit()

            if not client_id:
                register_client_domain = RegisteredClientDataTable(
                    client_name=client_name, client_domain=domain_name
                )
                session.add(register_client_domain)
                session.commit()
                client_id = register_client_domain.client_id

            is_email_id_registered = (
                session.query(ClientLoginTable).filter_by(email_id=email_id).first()
            )

            if is_email_id_registered:
                return (
                    jsonify(
                        {
                            "message": f"User {email_id} already exists! Please use different email ID or login!"
                        }
                    ),
                    401,
                )

            new_user_signup_registration = ClientLoginTable(
                client_id=client_id, email_id=email_id, hashed_password=hashed_password
            )
            session.add(new_user_signup_registration)
            session.commit()

            return jsonify({"message": f"User {email_id} created successfully!"}), 200

        except Exception as err:
            return jsonify({"error": str(err)}), 500

    def client_login(self, email_id, plaintext_password):
        try:
            client_user = (
                session.query(ClientLoginTable)
                .filter(and_(ClientLoginTable.email_id == email_id))
                .first()
            )
            if client_user is None:
                return jsonify({"error": "Invalid email or password"}), 401

            if not bcrypt.verify(plaintext_password, client_user.hashed_password):
                return jsonify({"error": "Invalid email or password"}), 401

            client_id = client_user.client_id
            token = generate_token(email_id, client_id)
            return jsonify({"token": token}), 200

        except Exception as err:
            return jsonify({"error": str(err)}), 500

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
