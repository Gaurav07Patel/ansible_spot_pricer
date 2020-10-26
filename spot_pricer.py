import boto3
import json
import csv
import pprint

#creating csv file to store data
# csv_file = open('spotInstances.csv', 'w',encoding ='utf-8')
# csv_writer = csv.writer(csv_file)
# headerofcsv= ['InstanceType','SpotPrice','AvailabilityZone','Timestamp']
# csv_writer.writerow(headerofcsv)   
def awsApi():
    client=boto3.client('ec2',region_name='us-east-1')
    prices=client.describe_spot_price_history(
                                            InstanceTypes=['t2.micro'],
                                            MaxResults=20,
                                            ProductDescriptions=['Linux/UNIX (Amazon VPC)'])
    spot_data=prices['SpotPriceHistory']
    return spot_data

def azWithLowestPrice(spot_data):
    spot={}
    bestAz=''
    for instance in spot_data:
        price= float(instance['SpotPrice']) 
        az= instance['AvailabilityZone']
        if az not in spot.keys():
            spot[az]=price
        lowestPrice=min(spot.values())    
        for az,price in spot.items():
            if price==lowestPrice:
                bestAz=az
                break    
    lp=(str(lowestPrice))
    listWithPandA=[lp,bestAz]
    return listWithPandA

def imageID():
    client=boto3.client('ec2',region_name='us-east-1')
    image=client.describe_images(
        Filters=[
            {'Name': 'owner-id','Values': ['137112412989']}, 
            {'Name': 'description','Values': ['Amazon Linux 2 AMI 2.0.20200917.0 x86_64 HVM gp2']} 
        ]
    )     
    imageid= (image['Images'][0]['ImageId'])
    return imageid

def keyPairName():
    client=boto3.client('ec2',region_name='us-east-1')
    keypairs = client.describe_key_pairs()
    keyName= keypairs['KeyPairs'][0]['KeyName']
    return keyName

def InstanceType():
    instanceName=spot_data[0]['InstanceType']
    return instanceName

def securityGroup():
    client=boto3.client('ec2',region_name='us-east-1')
    sg = client.describe_security_groups(
        Filters= [{ 'Name':'group-name', 'Values' : ['default']}]
    )
    sGID=sg['SecurityGroups'][0]['GroupId']
    return sGID

def createSpotInstance(listWithPandA,imageid,keyName,instanceName,sGID):
    client=boto3.client('ec2',region_name='us-east-1')
    response = client.request_spot_instances(
        SpotPrice= listWithPandA[0],
        InstanceCount=1,
        Type='one-time',
        LaunchSpecification={
            'ImageId': imageid,
            'KeyName': keyName,                     
            'InstanceType': instanceName,
            'Placement': {
                'AvailabilityZone': listWithPandA[1],
            },
            'SecurityGroupIds': [
                sGID
            ]
        }
    )
    print(response)

if __name__ == "__main__":
    spot_data=awsApi()
    listWithPandA = azWithLowestPrice(spot_data)
    imageid=imageID()
    keyName= keyPairName()
    instanceName=InstanceType()
    sGID= securityGroup()
    createSpotInstance(listWithPandA,imageid,keyName,instanceName,sGID)