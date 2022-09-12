# printing terminal disableApiTermination
import boto3
region = 'us-east-1'
client = boto3.client('ec2' , region_name=region)

# Get the list of Instances :
ec2_resource=boto3.resource(service_name="ec2",region_name=region)

list_instances = []

for each in ec2_resource.instances.all():
    print(each.instance_id)
    list_instances.append(each.instance_id)

# From the list of Instance ID find terminal protection enabled
for each in list_instances:
    #response = client.describe_instance_attribute(Attribute='disableApiTermination',InstanceId ='i-0680bfac7a219190b')
    response = client.describe_instance_attribute(Attribute='disableApiTermination',InstanceId = each)
    print(response['DisableApiTermination']['Value'])
    result = (response['DisableApiTermination']['Value'])
    if result == False:
        print(each + "=="  "terminal protection is disabled")
    else:
        print(each + "=="  "terminal protection is enabled")
