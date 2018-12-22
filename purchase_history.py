import json
import pymysql
import datetime

rds_host  = "host_name"
name = "name"
password = "*****"
db_name = "db_name"

conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=10)


def lambda_handler(event, context):
    user = event['username']
    #user = 'aastha'
    res = []
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM Purchase_Details WHERE user=%s ', user)
        conn.commit()
        for i in cur:
            my_arr = {}
            my_arr['item'] = i[3]
            my_arr['date'] = i[5].strftime('%m/%d/%Y')
            
            res.append(my_arr)
        print(res)
        
        return {
            "results": res
        }
        