import boto3
import boto3.dynamodb.types

deserializer = boto3.dynamodb.types.TypeDeserializer()


class get_ddb_details:

    def __init__(self):
        #print(" #START# " + str(__class__.__name__))
        self.ddb_client = boto3.client('dynamodb',
                                        region_name='us-east-1')

    def get_ddb_items(self, table, ddbkey, feature):
        FUNC_NAME = ' get_ddb_items START ' 
        #print(
            # f'START {FUNC_NAME}: Fetching properties from Table: {table} for key: {ddbkey} and feature: {feature}')
        try:
            ddb_items = self.ddb_client.get_item(
                Key={
                    'key': {
                        'S': str(ddbkey),
                    },
                    'feature': {
                        'S': str(feature),
                    },
                },
                TableName=table,
            )
            converted_ddb_items = self.convert_ddbjson_to_dict(ddb_items)
            #print(f'END {FUNC_NAME}')
            #print(f'#END# {__class__.__name__}')
            return converted_ddb_items["value"]
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return e

    def convert_ddbjson_to_dict(self, data):
        try:
            deserializer_data = {k: deserializer.deserialize(
                v) for k, v in data["Item"].items()}
            return deserializer_data
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return e
