import pymysql
import datetime
import boto3
import re
import json


rds_host  = "host_name"
name = "name"
password = "*****"
db_name = "db_name"

conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=10)


def lambda_handler(event, context):

    #check for today's date
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    print(today)
    my_user = set()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM Next_Purchase WHERE dt=%s', '2018-12-21')
        conn.commit();
        
        for row in cur:
            print(row[1])
            my_user.add(row[1])
            
        client = boto3.resource('s3')
        print(my_user)
        for i in my_user:
            json_object = client.Object('usertokens',i)
            print(json_object)
            json_file_reader = json_object.get()['Body'].read()
            content = json.loads(json_file_reader)
            token=content['token']
            send_push(token,{'message':"You have an upcoming purchase"})
        #send notifications to those users
    
def send_push(device_id, body):
    #region = [r for r in boto3.sns.regions() if r.name==u'eu-east-1'][0]
    sns = boto3.client('sns',region_name='us-east-1')
    #sns = boto3.sns.SNSConnection()
    try:
        endpoint_response = sns.create_platform_endpoint(
            PlatformApplicationArn='arn:aws:sns:us-east-1:349081554385:app/GCM/Grocery_Notifications',
            Token=device_id,
        )   
        print(endpoint_response)
        endpoint_arn = endpoint_response['EndpointArn']
    except Exception as err:
        print("Exception ",err)
        '''
        result_re = re.compile(r'Endpoint(.*)already', re.IGNORECASE)
        result = result_re.search(err.message)
        if result:
            endpoint_arn = result.group(0).replace('Endpoint ','').replace(' already','')
        else:
            raise
        '''    
    #print("ARN:", endpoint_arn)
    
    publish_result = sns.publish(
        TargetArn=endpoint_arn,
        Message=body['message'],
    )

    print("PUBLISH")