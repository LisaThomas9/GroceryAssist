import pymysql

rds_host  = "host_name"
name = "name"
password = "*****"
db_name = "db_name"

conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=10)

def lambda_handler(event, context):
    #get user from the query string
    username = event['username']
    
    item_list = []
    #read the offers table and user purchase table and see if there are any offers
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor2 = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT item FROM Purchase_Details WHERE User=%s',username)
    res = []
    for i in cursor:
        print(i['item'])
        cursor2.execute("SELECT * FROM Offer where lower(item) LIKE %s ","%"+i['item'].lower()+"%")
        for j in cursor2:
            print(j)
            d = {}
            d['store'] = j['store']
            d['item'] = j['item']
            d['sale'] = j['sale']
            d['expiry'] = j['expiry']
            d['image'] = j['image']
            res.append(d)
    print(res)
    conn.commit()
    
    return {
        "results": res
    }
           
    
    
