import csv
import json
import time as tm
from selenium import webdriver

driver = webdriver.Chrome('/Users/lisa/Downloads/chromedriver')  #put path to chromedriver here
driver.get('https://mygrocerydeals.com/deals?q=&supplied_location=10027&latitude=40.8138912&longitude=-73.96243270000002&view=list');
#time.sleep(5) # Let the user actually see something!

tm.sleep(5)

deals = driver.find_elements_by_xpath("//*[@id='deals']/div[@data-type='special']")
print(len(deals))

data = {}  
data['deals'] = []  

'''
with open('weekly_offers.csv', mode='w') as out_file:
	writer = csv.writer(out_file, delimiter=',')
'''
for deal in deals:
	
	price = deal.find_element_by_xpath("./div[@class='tile-content']/div[2]/span[1]").text
	expiry = deal.find_element_by_xpath("./div[@class='tile-content']/div[2]/div[2]").text
	item = deal.find_element_by_xpath("./div[@class='tile-content']/div[3]/p[1]").text
	store = deal.find_element_by_xpath("./div[@class='tile-content']/div[3]/p[2]").text
	image = deal.find_element_by_xpath("./div[@class='tile-content']/div[1]/img").get_attribute("src")
	
	'''
	data['deals'].append({
			'store': store,
		    'item': item,
		    'sale': price,
		    'expiry': expiry
		})
	#writer.writerow([store, item, price, expiry])
	#print(price, expiry, item, store)
	'''
	data['deals'].append({
			'store': store,
		    'item': item,
		    'sale': price,
		    'expiry': expiry,
		    'image':image
		})
	

driver.quit()

with open('weekly_offers.txt', 'w') as outfile:  
    json.dump(data, outfile)