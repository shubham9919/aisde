import boto3
import json


class get_sm_details:

    def __init__(self):
        #print(" #START# " + str(__class__.__name__))
        self.sm_client = boto3.client('secretsmanager', 
                                      region_name='us-east-1')

    def get_sm_values(self, sm_name, sm_key):
        FUNC_NAME = " get_sm_values "
        #print(
            # f'START {FUNC_NAME}: Fetching details for secret name: {sm_name} and secret key: {sm_key}')
        try:
            response = self.sm_client.get_secret_value(
                SecretId=str(sm_name)
            )
            return self.extract_secret_string(response)
        except Exception as e:
            #print(f'ERROR: {str(e)}')
            return e

    def extract_secret_string(self, sm_val):
        FUNC_NAME = " extract_secret_string "
        #print(
            # f'START {FUNC_NAME}: extracting secrets and transforming values from string to dict')
        try:
            transformed_secrets = json.loads(sm_val["SecretString"])
            secrets_dict = {key: json.loads(
                value) for key, value in transformed_secrets.items()}
            #print(f'END {FUNC_NAME}')
            return secrets_dict
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return e
