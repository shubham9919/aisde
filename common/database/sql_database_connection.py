"""
Connections to SQL Databases
"""

from sqlalchemy import create_engine, MetaData
from aws_common.utils.common import common_utils
from common.pipeline.utils import read_config_file

class CyberDatabase:
    def __init__(self):
        self.aws_configs = common_utils('cyber').get_common_properties()
        self._config = read_config_file()
        self._uri = self.aws_configs['rds_connection_secrets']["host"]
        self._port = self.aws_configs['rds_connection_secrets']["port"]
        self._database_type = self.aws_configs["rds_connection_secrets"]["dbType"]
        self._database_name = self.aws_configs["rds_connection_secrets"]["dbname"]
        self._schema = self.aws_configs["rds_connection_secrets"]["schema"]
        self._username = self.aws_configs["rds_connection_secrets"]["user"]
        self._password = self.aws_configs["rds_connection_secrets"]["password"]
        self._engine = create_engine(f'{self._database_type}://{self._username}:'
                                     f'{self._password}@{self._uri}:{self._port}/{self._database_name}', echo=False)

        self._metadata = MetaData(self._engine, schema=self._schema)
        print(self.aws_configs)

    def engine(self):
        return self._engine

    def metadata(self):
        return self._metadata
    
    def common_props(self):
        return self.aws_configs
