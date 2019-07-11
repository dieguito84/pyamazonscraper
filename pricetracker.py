import os
import re
import requests
import sqlite3

from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"

SQL_CREATE_PRODUCTS_TABLE = '''CREATE TABLE IF NOT EXISTS products (
                                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                                username varchar NOT NULL,
                                asin varchar NOT NULL,
                                url varchar NOT NULL,
                                title varchar NOT NULL,
                                price float NOT NULL,
                                rating float,
                                is_deal bolean NOT NULL,
                                deal_expiry_time datetime,
                                last_check datetime,
                                price_diff float
                                );'''

# I will use BeautifulSoup over requests-html because of performance and compatibility with Python 3.5

# TODO: think the entire application with Telegram Bot integration in mind
# TODO: use SQLite to store url to check, product details, users data for notifications

# SQLite tables fields:
# unique id (autoincrement, primary key) - int
# user identifier (telegram nickname?) - varchar
# product asin - varchar
# product url (shortened in some way, until asin) - varchar
# product title - varchar
# product price - float
# product rating - float if present, int 0 if not present
# is deal - int 0 = no, int 1 = yes
# deal expiry time - int 0 if not present, datetime if present
# last check - int 0 if not present, datetime if present
# price difference from last check - float

# TODO: evaluate if it is better to create a table for each user instead of a single table for every user and product

class PriceTracker:
    '''
    Amazon.it price tracker.
    '''

    def html(self, url, user_agent=USER_AGENT):
        '''
        Get HTML code for given URL.
        '''
        self.url = url
        self.user_agent = user_agent
        self.page = requests.get(self.url ,headers={"User-Agent": self.user_agent})
        self.soup = BeautifulSoup(self.page.content, "html.parser")

        return self.soup
    
    def title(self, html):
        '''
        Parser to find product's title.
        '''
        self._title = html.find(id="productTitle").get_text().strip()

        return self._title
    
    def price(self, html):
        '''
        Parser to find product's price.
        '''
        try:
            self._price = html.find(id="priceblock_ourprice").get_text()    # normal price
        except AttributeError:
            self._price = html.find(id="priceblock_dealprice").get_text()    # deal price
        
        return self._price
    
    def rating(self, html):
        '''
        Parser to find product's rating.
        '''
        self._rating_full = html.find(id="averageCustomerReviews")    # get a wide section to refine the search later
        try:
            self._rating = self._rating_full.find(class_="a-icon-star").get_text()   # search refined - with value (there are reviews)
        except AttributeError:
            self._rating = None    # without value (there are not reviews)
        
        return self._rating
    
    def is_deal(self, html):
        '''
        Check if the product is a deal.
        '''
        if html.find(id="priceblock_dealprice"):
            return True
        else:
            return False
    
    def deal_expiry_time(self, html):
        '''
        Get time remaining for a deal.
        '''
        if pt.is_deal(page) == True:    # first check if is a deal using is_deal method
            try:
                self._deal_expiry_time = html.find(id=re.compile("deal_expiry_time")).get_text()    # used re.compile to find a piece of string through regular expression
                return self._deal_expiry_time[13:]    # remove "Termina tra "
            except AttributeError:    # deal_expiry_time without value (it's not a timed offer)
                return None
        else:    # if is not a deal just return None
            return None
    

class Product:
    '''
    Basic product details.
    '''

    def __init__(self, url, title, price, rating, is_deal=False, deal_expiry_time=None):
        '''
        Object constructor.
        '''
        self.url = url
        self.title = title
        self.price = price
        self.rating = rating
        self.is_deal = is_deal
        self.deal_expiry_time = deal_expiry_time
    
    def details(self):
        '''
        Print product details.
        '''
        print("L'URL dell'articolo è " + self.url)
        print("Il titolo dell'articolo è " + self.title)
        if self.is_deal == True:
            if self.deal_expiry_time != None:
                print("Il prezzo dell'articolo è " + self.price + " e si tratta di un'offerta che termina tra " + self.deal_expiry_time)
            else:
                print("Il prezzo dell'articolo è " + self.price + " e si tratta di un'offerta")
        else:
            print("Il prezzo dell'articolo è " + self.price)
        
        if self.rating != None:
            print("La valutazione dell'articolo è " + self.rating)
        else:
            print("Non ci sono recensioni")


# TODO: evaluate if it is better to split database management into a standalone module (db.py?)
class Database (object):
    '''
    Database management.
    '''

    def __init__(self, db_file):
        '''
        Object constructor.
        '''
        self.db_is_new = not os.path.exists(db_file)
        self.db = sqlite3.connect(db_file)
        self.db_file = db_file    # is it really useful?
        if self.db_is_new:
            self.create_table(SQL_CREATE_PRODUCTS_TABLE)
    
    def create_table(self, create_table_sql):
        '''
        Table creation.
        '''
        self.cursor = self.db.cursor()
        self.cursor.execute(create_table_sql)
    
    def select(self):
        '''
        Show row content.
        '''
        # TODO: find a way to generalize select method (use it with different queries)
        pass
        # code to show row content
    
    def select_all(self):
        '''
        Show all rows content.
        '''
        select_all_command = '''SELECT * FROM products'''
        self.cursor = self.db.cursor()
        self.cursor.execute(select_all_command)

        rows = self.cursor.fetchall()

        for row in rows:
            print(row)
    
    def insert(self, product):
        '''
        Insert row into the table.
        '''
        insert_command = '''INSERT INTO products(username,asin,url,title,
                            price,rating,is_deal,deal_expiry_time,
                            last_check, price_diff)
              VALUES(?,?,?,?,?,?,?,?,?,?)'''
        self.cursor = self.db.cursor()
        self.cursor.execute(insert_command, product)

        return self.cursor.lastrowid
    
    def update(self, product):
        '''
        Update row content.
        '''
        # TODO: find a way to generalize update method (different fields and conditions)
        update_command = '''UPDATE products SET last_check = ?
                            WHERE id = ?'''
        self.cursor = self.db.cursor()
        self.cursor.execute(update_command, product)
    
    def delete(self, product):
        '''
        Delete row.
        '''
        delete_command = '''DELETE FROM products WHERE id = ?'''
        self.cursor = self.db.cursor()
        self.cursor.execute(delete_command, product)
    
    def commit(self):
        '''
        Commit changes to database
        '''
        self.db.commit()
    
    def disconnect(self):
        '''
        Disconnect from database.
        '''
        self.db.close()


pt = PriceTracker()

page = pt.html("https://www.amazon.it/Rowenta-Smart-Force-Essential-Aspirapolvere/dp/B07BCNBZX8/ref=gbps_tit_s-5_1669_45c55016?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=9APEYZYZMMXHPN5SY7ZQ")

url = "https://www.amazon.it/Rowenta-Smart-Force-Essential-Aspirapolvere/dp/B07BCNBZX8/ref=gbps_tit_s-5_1669_45c55016?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=9APEYZYZMMXHPN5SY7ZQ"

obj = Product(url, pt.title(page), pt.price(page), pt.rating(page), pt.is_deal(page), pt.deal_expiry_time(page))

obj.details()

# TODO: check why is it possible to insert text value into float field (obj.price and obj.rating)
# TODO: validate data type before insert into database fields
# TODO: create a function to get product's ASIN code (put it inside PriceTracker class and then use it in Product class)
db = Database("pricetracker.sqlite3")

product = ("dieguito84", "ABCDE12345", obj.url, obj.title, obj.price, obj.rating, obj.is_deal, obj.deal_expiry_time, "2019-07-06", "4")
#db.insert(product)

product_update = ("2019-07-10", "1")
db.update(product_update)

db.commit()

db.select_all()

db.disconnect()