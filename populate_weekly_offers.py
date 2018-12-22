import pymysql
import json 
import boto3

rds_host  = "host_name"
name = "name"
password = "*****"
db_name = "db_name"

conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=10)

def lambda_handler(event, context):
    
    s3 = boto3.resource('s3')
    
    content_object = s3.Object('weeklyoffers', 'weekly_offers.txt')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    vals = []
    for i in json_content['deals']:
        a = [i['store'], i['item'], i['sale'], i['expiry'], i['image']]
        vals.append(a)
    
    print(vals)
    
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO Offer(store, item, sale, expiry, image) VALUES (%s, %s, %s,%s, %s)", vals)
        conn.commit()
