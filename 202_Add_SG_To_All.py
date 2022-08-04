##https://stackoverflow.com/questions/39352349/boto3-attach-detach-security-group-from-ec2-instance

import boto3
region = 'us-west-1
ec2 = boto3.resource('ec2' , region_name=region)

# get security group id that you wanted to add/remove from the instances.

sg_id = input("Please put the Security Group_ID that you would like to apply to all the EC2 Instaces")
#sg_id = "sg-061a9a05c341932cc"

vpc_id = input("Which VPC-ID this Security Group Needs to Apply: Please Specify vpc-id ")

vpc_filter = [{'Name': 'vpc-id','Values': [vpc_id]}]

#vpc_filter = [{'Name': 'vpc-id','Values': ['vpc-02a64cb8c128d28b7']}]

#Multi_vpc_filter = [{'Name': 'vpc-id','Values': ['vpc-08c9d2f2c3820e13d','vpc-06aaeeefe4c18bfa3','vpc-0f38a784118d53c13']}]

############################################################################
"To Add the SG to All the Instances in specific vpc using vpc_filter"
#############################################################################

# filter instances per VPC as Security Group is specific to the VPC 
instances = ec2.instances.filter(Filters=vpc_filter)

for instance in instances:
    print(instance.id, instance.instance_type,instance.private_ip_address)
    all_sg_ids = [sg['GroupId'] for sg in instance.security_groups]  # Get a list of ids of all securify groups attached to the instance
    #print(all_sg_ids)
    if sg_id in all_sg_ids:                                          # Check the SG to be Applied is in the list
            print('Security Group is already applied to' + instance.private_ip_address )               # Print SG is already there 
    elif len(all_sg_ids) == 5:
            print(instance.private_ip_address + "has already 5 security groups")
    else:
            all_sg_ids.append(sg_id)                                 # Add the SG to the List
            instance.modify_attribute(Groups=all_sg_ids)             # Attach the list SGs to the instance
            print("modified sg to this ip: " + instance.private_ip_address + "instace_id:"+ instance.id )


