from common.config_constants import CYBER_SCHEMA_NAME
from common.database.sql_create_connection import cyber_db
from common.database.sql_database_connection import CyberDatabase
from common.database.sql_models import Base

from sqlalchemy.orm import Session


cyber_db = CyberDatabase()
session = Session(cyber_db.engine())
session.execute(f"SET search_path TO {CYBER_SCHEMA_NAME}")
session.commit()
Base.metadata.create_all(cyber_db.engine())
session.close()
