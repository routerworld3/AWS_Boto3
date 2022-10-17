#https://github.com/mark-bixler/aws-ec2-ssm-inventory
"""
Return set of EC2 Instances Managed by SSM
"""
import csv
import logging
import boto3
import botocore
from boto3.session import Session

# Define Environment Variables
DEFAULT_SESSION = boto3.Session(profile_name='default')
DEFAULT_CLIENT = DEFAULT_SESSION.client('sts')
REGIONS = ['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2']
ORG_ACCOUNT = '12345678901'
AWS_ROLE = 'yourAwsRole'
INVENTORY = {}
COLS = []

# Set Logger

logging.basicConfig(format='%(asctime)s %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p',
                filename='./logs/inventory.log',
                filemode='w',
                level=logging.INFO)

####################################################################################################
# MAIN FUNCTION
def main():
    """Main Function to Grab EC2 Inventory"""

    account_list = get_all_accounts()

    for account in account_list:
        for region in REGIONS:
            print("Account {} --> Region {}".format(account, region))

            # Get New SSM Client
            ssm_client = get_new_client(account, 'ssm', region)

            # Test Client For Blank ssm_client
            # "None" means no permissions on current account
            if ssm_client is None:
                # Get Next Account
                continue

            # Grab SSM Managed Instances
            ssm_instances = get_ssm_instances(ssm_client)

            # List for Just SSM Instances for later comparison
            ssm_instances_list = []

            for instance in ssm_instances:
                # Test Flag for Security Agent
                num = 0

                # Store Instance ID for later comparison
                ssm_instances_list.append(instance[0]['InstanceId'])

                # Grab Instance Application Inventory
                inventory_response = ssm_client.list_inventory_entries(
                    InstanceId=instance[0]['InstanceId'],
                    TypeName='AWS:Application'
                )
                for entry in inventory_response['Entries']:
                    try:
                        if entry['Name'] == 'ESET File Security' or \
                            entry['Name' == 'CrowdStrike Windows Sensor']:
                            num += 1

                    except (KeyError, ValueError):
                        logging.info("Instance Doesn't have Secuirty Software Installed: %s",
                                      instance)
                        continue

                # Check If Security Agent is Installed
                if num > 0:
                    compliant_value = 'TRUE'
                else:
                    compliant_value = 'FALSE'

                INVENTORY[instance[0]['InstanceId']] = {
                    'ComputerName':instance[0]['ComputerName'],
                    'Account':account,
                    'Region':region,
                    'InstanceId':instance[0]['InstanceId'],
                    'IpAddress':instance[0]['IpAddress'],
                    'PlatformType':instance[0]['PlatformType'],
                    'PlatformName':instance[0]['PlatformName'],
                    'SSM_Managed':'TRUE',
                    'Compliant':compliant_value
                    }

            # Get EC2 Client
            ec2_client = get_new_client(account, 'ec2', region)

            # Grab All Instances
            all_instances = get_all_instances(ec2_client)

            # Compare SSM Instances Against All Instances
            for ec2_instance in all_instances:
                ec2_platform = 'other'
                ec2_name = '<emtpy>'
                ec2_compliant = 'FALSE'
                ec2_prvtip = '<empty>'

                if ec2_instance['InstanceId'] not in ssm_instances_list:
                    # Check for Platform Entry
                    try:
                        ec2_platform = ec2_instance['Platform']
                    except (KeyError, ValueError):
                        logging.info("Instance %s Doesn't have a platform type.",
                                      ec2_instance['InstanceId'])

                    # Check for Private IP Entry
                    try:
                        ec2_prvtip = ec2_instance['PrivateIpAddress']
                    except (KeyError, ValueError):
                        logging.info("Instance %s Doesn't have a private ip.",
                                      ec2_instance['InstanceId'])
                    # Loop Through Tags
                    try:
                        for tag in ec2_instance['Tags']:
                            if tag['Key'] == 'Name':
                                ec2_name = tag['Value']

                    except (KeyError, ValueError):
                        logging.info("Instance %s doesn't have Tags",
                                      ec2_instance['InstanceId'])

                    INVENTORY[ec2_instance['InstanceId']] = {
                        'ComputerName':ec2_name,
                        'Account':account,
                        'Region':region,
                        'InstanceId':ec2_instance['InstanceId'],
                        'IpAddress':ec2_prvtip,
                        'PlatformType':ec2_platform.capitalize(),
                        'PlatformName':'<empty>',
                        'SSM_Managed':'FALSE',
                        'Compliant':ec2_compliant
                        }

####################################################################################################
# Get AWS Credentials
def get_new_client(account_id, resource, region):
    """Return temp creds for each account"""

    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.
    try:
        response = DEFAULT_CLIENT.assume_role(
            RoleArn="arn:aws:iam::" + account_id + ":role/" + AWS_ROLE,
            RoleSessionName="AssumeRoleSession1"
            )

        session = Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                      aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                      aws_session_token=response['Credentials']['SessionToken'],
                      region_name=region)

        return session.client(resource)

    except botocore.exceptions.ClientError as e:
        logging.info("Error: %s", e)

####################################################################################################
# Get Non-Terminated Instances
def get_ssm_instances(ssm_client):
    """Return SSM Managed Instances for Further Processing"""

    logging.info('Getting SSM Inventory')

    # Utilize SSM Paginator
    paginator = ssm_client.get_paginator('get_inventory')
    response_iterator = paginator.paginate()

    # Initialize Instance List
    instances = []

    ## Loop Through Inventory in each Account
    for inventory in response_iterator:
        for entity in inventory['Entities']:
            try:
                instance = entity['Data']['AWS:InstanceInformation']['Content'][0]

                # Skip Terminated Instances
                if instance.get('InstanceStatus') == 'Terminated':
                    logging.info('Ignoring terminated instance: %s', entity)
                    continue

                # Update Inventory with Each Instance
                instances.append(entity['Data']['AWS:InstanceInformation']['Content'])

            except (KeyError, ValueError):
                logging.info('SSM inventory entity not recognised: %s', entity)
                continue
    return instances
####################################################################################################
# Get All Accounts
def get_all_accounts():
    """Return ALL Accounts"""

    # Set Account List
    account_list = []

    # Authenticate Client
    org_client = get_new_client(ORG_ACCOUNT, 'organizations', 'us-west-2')
    org_paginator = org_client.get_paginator('list_accounts')

    # Iterate Through Account List
    org_iterator = org_paginator.paginate()
    for accounts in org_iterator:
        for account in accounts['Accounts']:
            if account['Status'] == 'ACTIVE':
                account_list.append(account['Id'])

    return account_list

####################################################################################################
# Get All Account Instances
def get_all_instances(ec2_client):
    """Return ALL Instances to Compare against SSM"""
    logging.info('Getting SSM Inventory')

    # Utilize SSM Paginator
    paginator = ec2_client.get_paginator('describe_instances')

    response_iterator = paginator.paginate(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values' :['running', 'stopped']
            }]
    )

    # Initialize Instance List
    ec2_instances = []

    ## Loop Through Inventory in each Account
    for reservations in response_iterator:
        for instances in reservations['Reservations']:
            ec2_instances.append(instances['Instances'][0])

    # Send back list of Instances
    return ec2_instances

####################################################################################################
# Create CSV
def write_csv(filename):
    """Function to display results in CSV File"""

    # Set First Colum for Instance ID
    COLS.append('ResourceId')

    # Add Keys to be Columnns
    for key in INVENTORY:
        # Dynamically ADD Rest of Column Headings
        for item in INVENTORY[key]:
            if item not in COLS:
                COLS.append(item)

    # Open CSV For Writing Data
    with open(filename, 'w', newline='') as myfile:
        writer = csv.writer(myfile, delimiter=',')
        writer.writerow(COLS)
        for data in INVENTORY:
            # Add the ID of the Instance as the first item
            row = [data]
            listof_columns = INVENTORY[data]

            # Write Data to CSV
            itercols = iter(COLS)
            next(itercols)
            for col in itercols:
                if col in listof_columns:
                    row.append(listof_columns[col])
                else:
                    row.append("")
            writer.writerow(row)

####################################################################################################
main()

write_csv(("./output/master.csv"))
