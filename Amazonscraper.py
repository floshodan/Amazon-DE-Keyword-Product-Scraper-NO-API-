from selenium import webdriver
import MySQLdb
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

#database ajust
db = MySQLdb.connect(host="host",
                     user="user",
                     passwd="password",
                     db="databasename", use_unicode=True, charset="utf8")

cursor = db.cursor()

#get webbrowser
browser = webdriver.Chrome('/path/to/chromedriver')

cursor.execute("SELECT keyword FROM db_name WHERE status = 0")
keywords = cursor.fetchall()


for i in range(len(keywords)):
    asinl = []
    browser.get('http://amazon.de')
    browser.find_element_by_id("twotabsearchtextbox").send_keys(keywords[i])
    browser.find_element_by_class_name("nav-input").click()
    print(keywords[i])
    for j in range(39):
        try:
            asin = browser.find_element_by_id("result_{}".format(j)).get_attribute('data-asin')
        except NoSuchElementException:
            pass
        try:
            asin = browser.find_element_by_xpath('//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div[{}]'.format(j+1)).get_attribute('data-asin')
        except NoSuchElementException:
            break
        asinl.append(asin)
        cursor.execute("SELECT keyword FROM amazon2 WHERE status = 3")
    for k in range(len(asinl)):
        print(asinl[k])
        cursor.execute("SELECT keyword FROM amazon2 WHERE status = 3")
        browser.get('http://amazon.de/dp/'+asinl[k])

        try:
            title = browser.find_element_by_id('productTitle').text
        except NoSuchElementException:
            try:
                title = browser.find_element_by_id('ebooksProductTitle').text
            except NoSuchElementException:
                continue


        title = title.replace('"', "'")
        print(title)
        try:
            price = browser.find_element_by_id('priceblock_ourprice').text
        except NoSuchElementException:
            price = "0"
        print(price)
        try:
            img = browser.find_element_by_id('landingImage').get_attribute('data-a-dynamic-image')
        except NoSuchElementException:
            img = '"0"'
        start_pt = img.find("\"")
        end_pt = img.find("\"", start_pt + 1)  # add one to skip the opening "
        img_url = img[start_pt + 1: end_pt]
        print(img_url)
        try:
            descipt = browser.find_element_by_xpath('//*[@id="productDescription"]/p').text
        except NoSuchElementException:
            descipt = ""
        try:
            bullet = browser.find_element_by_id('feature-bullets').text
        except NoSuchElementException:
            bullet = ""
        bullet = bullet.replace('"', "'")

        try:
            stars = browser.find_element_by_xpath('//*[@id="detail_bullets_id"]/table/tbody/tr/td/div/ul/li[7]/span/span[1]/a[2]/i/span').get_attribute('innerHTML')
        except NoSuchElementException:
                try:
                    stars = browser.find_element_by_xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span').get_attribute('innerHTML')
                except NoSuchElementException:
                    stars = "0"

        try:
            bewertung = browser.find_element_by_xpath('//*[@id="acrCustomerReviewText"]').get_attribute('innerHTML')
        except NoSuchElementException:
            try:
                bewertung = browser.find_element_by_xpath('//*[@id="detail_bullets_id"]/table/tbody/tr/td/div/ul/li[4]/span/span[3]/a').get_attribute('innerHTML')
            except NoSuchElementException:
                bewertung = "0 Kundenrezessionen"
        print(stars)
        print(bewertung)
        #print(descipt)
        keyword = ''.join(keywords[i])
        sql = ('UPDATE db_name SET asin{0}="%s", title{0}="%s", price{0}="%s", img_url{0}="%s", bullet{0}="%s", stars{0}="%s", bewertung{0}="%s", status = 2 WHERE keyword = "%s"'.format(k+1) %(asinl[k], title, price, img_url, bullet, stars, bewertung, keyword))
        print(sql)
        cursor.execute(sql)
        db.commit()

db.close()
