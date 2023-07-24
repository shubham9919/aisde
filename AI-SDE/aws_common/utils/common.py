from .. import constants
from ..features.get_ddb_details import get_ddb_details
from ..features.get_sm_details import get_sm_details
import json


class common_utils:

    def __init__(self, project):
        self.COMMON = {}
        self.project = str(project)
        # common properties to load for all projects.
        self.sm_key = ""
        self.sm_name = ""
        self.project_properties_feature = ""
        self.project_properties_key = ""
        #print(
        #    f'Start {__class__.__name__} fetach properties for {project} project.')

    def get_common_properties(self):
        FUNC_NAME = ' get_common_properties '
        #print(f'#START# {FUNC_NAME}: Fetching common properties')
        try:
            ## setting DDB fetch values for COMMON:COMMON 
            table = constants.COMMON_DDB['TABLE']
            key = constants.COMMON_DDB['KEY']
            feature = constants.COMMON_DDB['FEATURE']

            # Loading COMMON:COMMON Item from visionbox_common table
            ddb_items = get_ddb_details().get_ddb_items(table, key, feature)

            # Getting project specific keys and features to load secrets and other properties.
            self.sm_name = ddb_items.get(self.project)["secret_name"]
            self.sm_key = ddb_items.get(self.project)["secret_key"]
            self.project_properties_key = ddb_items.get(
                self.project)["project_properties_key"]
            self.project_properties_feature = ddb_items.get(
                self.project)["project_properties_feature"]

            ## start fetching SM details ##
            if self.project == 'cyber':
                sm_values = get_sm_details().get_sm_values(self.sm_name, self.sm_key)
                # *Revisit* if database gonna be common then, will load only one DB secret and play around schema names from different projects
                db_details = sm_values.get('cyberdb')
                rds_connection_props = {
                    "host": db_details["host"],
                    "port": db_details["port"],
                    "dbname": db_details["dbname"],
                    "user": db_details["user"],
                    "password": db_details["password"],
                    "schema": db_details["schema"],
                    "dbType": db_details["dbType"]
                }

                self.COMMON.update(rds_connection_secrets=rds_connection_props)

                # start fetaching project specific properties
                project_properties = get_ddb_details().get_ddb_items(
                    table, self.project_properties_key, self.project_properties_feature)
                if project_properties.keys():
                    if 'buildwith_endpoints' in project_properties.keys():
                        self.COMMON.update(
                            buildwith_endpoints=project_properties["buildwith_endpoints"])
                    if 'buildwith_secrets' in project_properties.keys():
                        sm_props = project_properties["buildwith_secrets"]
                        if sm_props['sm_name'] == self.sm_name:
                            self.COMMON.update(
                                buildwith_secrets=sm_values.get("buildwith"))
                        else:
                            bw_secrets = get_sm_details().get_sm_values(
                                sm_props['sm_name'], sm_props['sm_key'])
                            buildwith_props = json.loads(
                                bw_secrets['buildwith_secrets'])
                            self.COMMON.update(
                                buildwith_secrets=buildwith_props)
                    if "mongodb_secrets" in project_properties.keys():
                        sm_props = project_properties["mongodb_secrets"]
                        if sm_props['sm_name'] == self.sm_name:
                            self.COMMON.update(
                                mongodb_secrets=sm_values.get("mongodb"))
                        else:
                            mg_secrets = get_sm_details().get_sm_values(
                                sm_props['sm_name'], sm_props['sm_key'])
                            mongodb_secrets = json.loads(mg_secrets['mongodb'])
                            self.COMMON.update(mongodb_secrets=mongodb_secrets)
                    if "jwt_secrets" in project_properties.keys():
                        sm_props = project_properties["jwt_secrets"]
                        if sm_props['sm_name'] == self.sm_name:
                            self.COMMON.update(
                                jwt_secrets=sm_values.get("jwt"))
                        else:
                            jwt_secrets = get_sm_details().get_sm_values(
                                sm_props['sm_name'], sm_props['sm_key'])
                            jwt_secrets = json.loads(mg_secrets['jwt'])
                            self.COMMON.update(jwt_secrets=jwt_secrets)
            else:
                print(f'Project: {self.project} not yet integrated with AWS')
                
            # dont #print rds_connection_props until masking logic to mask details is implemented

            return self.COMMON
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return e
