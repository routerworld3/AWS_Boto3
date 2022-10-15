#https://stackoverflow.com/questions/66085408/how-generate-ec2-inventory-from-multiple-aws-account-using-python-boto3
import boto3

session = boto3.Session(profile_name='dev')
ec2 = session.client('ec2', region_name='ap-south-1')
response = ec2.describe_instances()

import datetime
import csv
time = datetime.datetime.now().strftime ('%Y-%m-%d-%H-%M-%S')
filename_describe_instances = ('ec2_inventory_me-south-1_' + time + '.csv')
fieldnames = ['Instance_Name','ImageId', 'InstanceId', 'InstanceType', 'Availability_Zone', 'Platform', 'PrivateIpAddress','PublicIpAddress', 'State', 'SubnetId','VpcId', 'Environment', 'AccountId']



with open(filename_describe_instances, 'w', newline='') as csvFile:
    writer = csv.writer(csvFile, dialect='excel')
    writer.writerow(fieldnames)
    for Reserv in response['Reservations']:
        for Insta in Reserv['Instances']:
            instance_imageid = Insta.get('ImageId', 'NULL')
            instance_InstanceId = Insta.get('InstanceId', 'NULL')
            instance_InstanceType = Insta.get('InstanceType', 'NULL')
            instance_Availability_Zone = Insta['Placement'].get('AvailabilityZone', 'NULL')
            instance_Platform = Insta.get('Platform', 'Linux')
            instance_Private_IP = Insta.get('PrivateIpAddress', 'NULL')
            instance_Public_IP = Insta.get('PublicIpAddress', 'NULL')
            instance_State = Insta['State'].get('Name', 'NULL')
            instance_Subnet = Insta.get('SubnetId', 'NULL')
            instance_VPCID = Insta.get('VpcId', 'NULL')
            instance_OwnerId = Reserv.get('OwnerId', 'NULL')

            tags_list = []
            for n in Insta.get('Tags', 'NULL'):
                if n.get('Key', 'NULL') == 'Name':
                    instance_Name = n.get('Value', 'NULL')
                if n.get('Key', 'NULL') == 'Environment':
                    instance_Environment = n.get('Value', 'NULL')

            raw = [instance_Name,
                   instance_imageid,
                   instance_InstanceId,
                   instance_InstanceType,
                   instance_Availability_Zone,
                   instance_Platform,
                   instance_Private_IP,
                   instance_Public_IP,
                   instance_State,
                   instance_Subnet,
                   instance_VPCID,
                   instance_Environment,
                   instance_OwnerId]

            writer.writerow(raw)
            for o in raw:
                o = 'NULL'
            raw = []

csvFile.close()

########################################################################
# set up your .csv writer, etc outside the loop

# iterate over your profiles
profiles = ['Dev', 'Test', 'DevOps', 'Prepared', 'Prod']

for name in profiles:
    session = boto3.Session(profile_name=name)
    ec2 = session.client('ec2')
    response = ec2.describe_instances()
    #format your row and write to the .csv
###################################################################
accounts = ['123...789', '234...890',]
sts = boto3.client('sts') #assumes you have a default profile set
for id in accounts:
    role_arn = f'arn:aws:iam::{id}:role/Inventory'
    creds = sts.assume_role(role_arn=role_arn, role_session_name='some-name')
    session = boto3.Session(aws_access_key_id=creds['AccessKeyId'], ...)
    ec2 = session.client('ec2')