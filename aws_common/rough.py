import json
import boto3.dynamodb.types
import boto3

# x = "cyber"
# COMMON_DDB = {
#   'TABLE': 'visionbox_common', #Table name in dynamoDB
#   'KEY': 'COMMON', #key
#   'FEATURE': 'COMMON' #feature
    
# }
# print("fetching props for " + COMMON_DDB['KEY'])


# class get_ddb_details:

#     def __init__(self):
#         print("#START#" + str(__class__.__name__))

#     def demo(self): 
#         print(str(demo.__name__))

# d = get_ddb_details().demo()
deserializer = boto3.dynamodb.types.TypeDeserializer()

data = {'Item': {'value': {'M': {'cyber': {'M': {'secret_key': {'S': 'cyberdb'}, 'project_properties_feature': {'S': 'PROPERTIES'}, 'secret_name': {'S': 'CYBER'}, 'project_properties_key': {'S': 'CYBER'}}}}}, 'key': {'S': 'COMMON'}, 'feature': {'S': 'COMMON'}}, 'ResponseMetadata': {'RequestId': '49GASB9OJ123G0H975BSHLJRKRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Fri, 03 Mar 2023 17:37:04 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '232', 'connection': 'keep-alive', 'x-amzn-requestid': '49GASB9OJ123G0H975BSHLJRKRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '4262608011'}, 'RetryAttempts': 0}}

python_data = {k: deserializer.deserialize(v) for k,v in data["Item"].items()}
project = "cyber"
print(python_data["value"][project])
