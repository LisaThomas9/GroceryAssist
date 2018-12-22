import boto3
import math
import pymysql
import difflib
from datetime import datetime
from datetime import timedelta


rds_host  = "host_name"
name = "name"
password = "*****"
db_name = "db_name"

conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=10)

def check(i):
        try:
            int(i)
            return True
        except:
            return False

def days_between(d1, d2):
    #d1 = datetime.strptime(d1, "%d/%m/%Y")
    #d2 = datetime.strptime(d2, "%d/%m/%Y")
    return abs((d2 - d1).days)
    
def predict_next_purchase(user, items):
    #fetch DB contents 
    #######items needs to be list
    

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute('SELECT * FROM Purchase_Details WHERE User=%s ORDER BY dt', user)
        conn.commit()
        
        d_items = {}
        for row in cur:
            if row['item'] in items:
                print(row)
                i = row['item']
                d_items[i] = d_items.get(i, []) + [row['dt']]
        
        for it in d_items:
            dates = d_items[it]
            print(dates)
            if len(dates)>1:
                print('length greater')
                day = []
                for i in range(1,len(dates)):
                    c = days_between(dates[i],dates[i-1]);
                    day.append(c)
                    print(c)
                    dd=math.floor(sum(day)/len(day))
                    print(dd)
                last_date = dates[-1] 
                
                #add the predicted interval to the last date
                next_date = last_date + timedelta(days=dd)
                print("Predicted date:", next_date,last_date)
                
                #put predictions into table
                cur.execute("INSERT INTO Next_Purchase(user, item, dt) VALUES (%s, %s, %s)", (user, it, next_date))
                conn.commit()
            

    
def lambda_handler(event, context):
    print("WORKING !!!")
    bucket='billsupload' 
    #photo='IMG_2644.JPG' ###change photo name
    photo = event['Records'][0]['s3']['object']['key']
    print(photo)
    
    client=boto3.client('rekognition')
    response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
    #response=client.detect_text(photo)
                        
    textDetections=response['TextDetections']
    user = photo #photo name is set to the user name
    
    j = 0
    k = 0
    items=[]
    quant = []
    item_name = []
    dateFound = 0
    store_name = ""
    food_items = ['milk','eggs','butter','sauce','sugar','bread','onion','curd','noodles','chocolate','waffle','salt','banana','cake','water']
    names = ["appletree", "keyfoods", "met","c-town","key","foods"]
    street_names = ["broadway","amsterdam","ave"]
    for text in textDetections:
        
        if text["Type"] == "WORD":
            print(text)
            txt = text['DetectedText']
            #print(txt)
            store_name1 = difflib.get_close_matches(txt.lower(),names)
            
            if store_name1:
                store_name = store_name1[0]
            if not dateFound:
                if "2018" in txt:
                    try:
                        if '-' in txt:
                            purchase_date = datetime.strptime(txt.replace(" ",""), '%Y-%m-%d').strftime('%Y-%m-%d')
                        elif '/' in txt:
                            purchase_date = datetime.strptime(txt.replace(" ",""), '%Y/%m/%d').strftime('%Y-%m-%d')
                    except:
                        purchase_date = "2018-12-15"
                    dateFound = 1
            if txt.lower() not in names and txt.lower() not in street_names:
                item_name1 = difflib.get_close_matches(txt.lower(),food_items)
                if item_name1:
                    k = j
                    item_nam = item_name1[0]
                    print("myyy",txt,item_nam,k)
                    item_name.append(item_nam)
                    
                if k+1 == j:
                    print("inside check :", txt)
                    x = len(item_name)
                    y = len(quant)
                    if x > y:
                        if y != x-1:
                            quant.extend([1]*(x-y-1))
                        checker = check(txt)
                        if checker:
                            quant.append(int(txt))
                        else:
                            quant.append(1)
    
                j += 1
                if "total" in txt.lower():
                    break
                
    
    print("Store Name :",store_name)
    print("Purchase date : ",purchase_date)
    print("items :",item_name)
    print("quant :",quant)
    items = zip(item_name, quant)
    print(items)
    
    vals = []
    for i,j in items:
        vals.append([user, store_name, i, j, purchase_date])
    
    print(vals)
    
    #put details in RDS
    
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO Purchase_Details(user, store, item, quantity, dt) VALUES (%s, %s, %s,%s,%s)", vals)
        conn.commit()
    '''
    item_name = ["milk", "bread"]
    user = "aastha"
    '''
    predict_next_purchase(user,item_name)
    
    
    
