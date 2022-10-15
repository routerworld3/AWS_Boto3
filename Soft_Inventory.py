#aws ssm list-inventory-entries --instance-id i-xxxxxxxxxxxx --type-name AWS:Application

import boto3
region = "us-east-1"

ssm_client = boto3.client('ssm',region)

response = ssm_client.list_inventory_entries(
    InstanceId ='i-0eb51d23d00909686',
    TypeName ='AWS:Application'
    )
print("inventory=", response)

soft_int = response['Entries'] 

for soft in soft_int:
    print(soft['Name'], soft ['Version'])

#dict_keys(['Architecture', 'InstalledTime/optional', 'Name', 'PackageId', 'Publisher', 'Version

# response.keys()   
# dict_keys(['TypeName', 'InstanceId', 'SchemaVersion', 'CaptureTime', 'Entries', 'ResponseMetad
#print(type(soft_int))
#<class 'list'>
