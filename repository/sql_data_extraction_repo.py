"""
Fetch Data using SQLAlchemy queries
"""

import datetime
import time
from datetime import timedelta

import numpy as np
import pandas as pd
from sqlalchemy import Table, select, bindparam, and_

from common.database.sql_database_connection import CyberDatabase


class CyberRepository:

    def __init__(self, engine, metadata):
        self.engine = engine
        self.metadata = metadata

    def get_data_from_table(self, table_name):

        df = pd.DataFrame()

        try:
            with self.engine.begin() as connection:
                cyber_table = Table(table_name, self.metadata, autoload=True, autoload_with=connection)

                query = select([cyber_table])
                all_rows = connection.execute(query).fetchall()

            df = pd.DataFrame(all_rows)
        except Exception as err:
            print(f'Here is the ERROR: \n{repr(err)}\nERROR IN CONNECTION OR ISSUE IN READING DATA {table_name}')

        return df


    def insert_data_into_table(self, table_name, data):
        pass

