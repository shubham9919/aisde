from pymongo import MongoClient

from common.pipeline.utils import read_config_file


class MongoDatabase:
    def __init__(self):
        self.config = read_config_file()["mongodb"]
        self.cluster = MongoClient(self.config["uri"])
        self.db = self.cluster[self.config["db_name"]]

    def get_cluster(self):
        return self.cluster

    def get_db(self):
        return self.db
