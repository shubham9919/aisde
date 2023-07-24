from common.database.sql_database_connection import CyberDatabase
from repository.sql_data_extraction_repo import CyberRepository

cyber_db = CyberDatabase()
cyber_repo = CyberRepository(cyber_db.engine(), cyber_db.metadata())
