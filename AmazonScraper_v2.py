import MySQLdb
import mysql.connector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import re
from random import randint
import random
import time
import json

#database
def db_connect():
	db = mysql.connector.connect(host="host",
                      user="user",
                      passwd="passwd",
                      db="db", use_unicode=True, charset="utf8", connect_timeout=600000)
	return db

db = db_connect()
cursor = db.cursor(dictionary=True)

cursor.execute("SELECT keyword FROM t1 WHERE status = 0")
db.close()


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome('/opt/chromedriver', chrome_options=chrome_options)



keywords = []
for row in cursor: 
	keywords.append((row['keyword']))

def get_asin(keyword, baseurl):
	time.sleep(3)
	asinl = []
	browser.get(baseurl)
	browser.find_element_by_id("twotabsearchtextbox").send_keys(keyword)
	browser.find_element_by_class_name("nav-input").click()

	asins = browser.find_elements_by_xpath('//*[@data-asin]')
	print(type(asins))
	#print(asins[0].get_attribute('data-asin'))
	for i in range(len(asins)):
		asin = asins[i].get_attribute('data-asin')
		asinl.append(asin)

	return asinl

def get_img():
	try:
		img = browser.find_element_by_id('landingImage').get_attribute('data-a-dynamic-image')
	except NoSuchElementException:
		img = '"0"'
	start_pt = img.find("\"")
	end_pt = img.find("\"", start_pt + 1)
	return img[start_pt + 1: end_pt]

def get_title():
	try:
		title = browser.find_element_by_id('productTitle').text
	except NoSuchElementException:
		title = ''
	return title

def get_price():
	try:
		price = browser.find_element_by_id('priceblock_ourprice').text
	except NoSuchElementException:
		try:
			price = browser.find_element_by_id('price_inside_buyboy').text
		except NoSuchElementException:
			price = '0'

	return price

def get_bullet():
	try:
			bullet = browser.find_element_by_id('feature-bullets').text
	except NoSuchElementException:
		try:
			bullet = browser.find_element_by_xpath('//*[@id="productDescription"]/p').text
		except NoSuchElementException:
			bullet = "leer"
	bullet = bullet.replace('"', "'")
	if (bullet is None or bullet == ''):
		bullet = "empty"
	
	return bullet

def get_stars():
	try:
		stars = browser.find_element_by_xpath('//*[@id="prodDetails"]/div[2]/div[2]/div[1]/div[2]/div/div/table/tbody/tr[2]/td[2]/span/span[1]/a[2]/i/span').text
	except NoSuchElementException:
		try:
			stars = browser.find_element_by_id('acrPopover').get_attribute('title')
		except NoSuchElementException:
			stars = '0'
	return stars

def get_reviews():
	try:
		reviews = browser.find_element_by_id('acrCustomerReviewText').text
	except NoSuchElementException:
		reviews = '0'
	return reviews

def get_info(keyword, asins, baseurl):
	info = {'keyword':keyword}
	for i in range(len(asins)):
		browser.get(f'{baseurl}/dp/{asins[i]}')
		time.sleep(3)
		bullet = get_bullet()
		info[f'asin{i+1}'] = asins[i]
		info[f'img{i+1}'] = get_img()
		info[f'title{i+1}'] = get_title()
		info[f'bullet{i+1}'] = bullet
		info[f'price{i+1}'] = get_price()
		info[f'stars{i+1}'] = get_stars()
		info[f'reviews{i+1}'] = get_reviews()
		info['items'] = i
  return info


## __main__:

def main():
	baseurl = 'http://amazon.de'
	for i in range(len(keywords)):
		print(keywords[i])
		asins = get_asin(keywords[i], baseurl)
		if not asins:
			continue
		print(asins)
		info = get_info(keywords[i], asins[:30], baseurl)
		print(info)
		db = db_connect()
		cursor = db.cursor(dictionary=True)
		sql = "INSERT INTO t1 (jdoc, status) VALUES (%s, 1) "
		sql2 = "UPDATE t1 SET jdoc= %s, status = 1 WHERE keyword = %s"
		val = (json.dumps(info), keywords[i])
		cursor.execute(sql2, val)
		db.commit()
		db.close()

main()

