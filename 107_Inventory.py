import boto3
import csv
import time

ec2_resource=boto3.resource(service_name="ec2",region_name="us-west-1")

#cnt=1                                         

file_str= time.strftime("%Y_%m_%d_%H_%M")
inv_file = "aws_inv_"+ file_str + ".csv"

csv_ob = open(inv_file,"w",newline='')
csv_w = csv.writer(csv_ob)                      

csv_w.writerow(["Instance_Id",'Instance_Name','Instance_Type','OS_TYPE','PRIVATE_IP','IAM_ROLE','IMAGE_ID','VPC','KEY','BOOT_MODE','SG','SG_ID'])


for each in ec2_resource.instances.all():
	all_sg_ids = [sg['GroupId'] for sg in each.security_groups]
	all_sg_name= [sg['GroupName'] for sg in each.security_groups]
	tag_value = [each_tag['Value'] for each_tag in each.tags if each_tag['Key'] == 'Name' ]
	name_tag=tag_value[0]
	csv_w.writerow([each.instance_id,name_tag,each.instance_type,each.platform_details,each.private_ip_address,each.iam_instance_profile,each.image_id,each.vpc_id,each.key_pair,each.boot_mode,all_sg_name,all_sg_ids])
	#cnt+=1
csv_ob.close()

####################################################################################################################################################
# for each in ec2_resource.instances.all():
	# csv_w.writerow([each.instance_id,each.instance_type,each.platform_details,each.private_ip_address,each.iam_instance_profile,each.image_id,each.vpc_id,each.key_pair,each.security_groups])
	#cnt+=1
# csv_ob.close()
# 
# 
##############################################################################################################################################
# 
# 
#Security_Groups is List of SG & Each SG is dictionary 
# all_sg_ids = [sg['GroupId'] for sg in each.security_groups]
# 
# 