import os
import re
import requests
import sqlite3

from bs4 import BeautifulSoup
from time import strftime

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"

# TODO: think the entire application with Telegram Bot integration in mind

# SQLite tables fields:
# unique id (autoincrement, primary key) - int
# user identifier (telegram nickname?) - varchar
# product asin - varchar
# product url (shortened in some way, until asin) - varchar
# product title - varchar
# product price - float
# product rating - float if present, int 0 if not present
# last check - datetime
# is deal - int 0 = no, int 1 = yes
# deal expiry time - int 0 if not present, datetime if present
# price difference from last check - float

# TODO: evaluate whether it is better to create a table for each user instead of a single table for every user and product

# TODO: maybe is it better to name this class "Parser"?
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
    
    def asin(self, url):
        '''
        Get product's ASIN from url.
        '''
        self.url = url

        search = re.search(r'(?<=/)B[A-Z0-9]{9}', url)    # starts with B, after that 9 characters, all just after a /
        
        return search.group(0)

    
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
        
        # TODO: should I transform it in float before returning it?
        return self._price[:-2].replace(",", ".")    # to remove " €" and replace "," with "." from price
    
    def rating(self, html):
        '''
        Parser to find product's rating.
        '''
        self._rating_full = html.find(id="averageCustomerReviews")    # get a wide section to refine the search later
        try:
            self._rating = self._rating_full.find(class_="a-icon-star").get_text()   # search refined - with value (there are reviews)
        except AttributeError:
            self._rating = None    # without value (there are not reviews)
        
        if self._rating is not None:
            # TODO: should I transform it in float before returning it?
            return self._rating[:3]    # return only first three characters of the rating (example: 4.0)
        else:
            return self._rating
    
    def last_check(self):
        '''
        Get current date and time.
        '''
        self._currentdatetime = strftime("%Y-%m-%d %H:%M:%S")    # format YYYY-MM-DD HH:MM:SS

        return self._currentdatetime
    
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
        if self.is_deal(html) == True:    # first check if is a deal using is_deal method
            try:
                self._deal_expiry_time = html.find(id=re.compile("deal_expiry_time")).get_text()    # used re.compile to find a piece of string through regular expression
                return self._deal_expiry_time[13:]    # remove "Termina tra "
            except AttributeError:    # deal_expiry_time without value (it's not a timed offer)
                return None
        else:    # if is not a deal just return None
            return None

    def price_diff(self, url, html):
        '''
        Get price difference from last check.
        '''
        _current_price = self.price(html)

        # should I refactor the _last_price retrieve?
        db = Database("pricetracker.sqlite3", "products")    # maybe will be useful to create a function for database initialization?
        _last_price = db.select("price", "products", "asin", (self.asin(url),))
        db.disconnect()

        return round(float(_current_price) - float(_last_price[0][0]), 2)    # round to 2 decimal places
        # TODO: maybe will be useful to return a list containing ["current price", "last price", "price difference"]


class Product:
    '''
    Basic product details.
    '''

    def __init__(self, url, asin, title, price, rating, last_check, is_deal=False, deal_expiry_time=None):
        '''
        Object constructor.
        '''
        self.url = url
        self.asin = asin
        self.title = title
        self.price = price
        self.rating = rating
        self.last_check = last_check
        self.is_deal = is_deal
        self.deal_expiry_time = deal_expiry_time
    
    def details(self):
        '''
        Print product details.
        '''
        print("L'URL dell'articolo è " + self.url)
        print("Il codice ASIN dell'articolo è " + self.asin)
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
        print("L'ultimo check è stato eseguito il " + self.last_check)


# TODO: evaluate whether it is better to split database management into a standalone module (db.py?)
class Database (object):
    '''
    Database management.
    '''

    def __init__(self, db_file, table):
        '''
        Object constructor.
        '''
        self.db_is_new = not os.path.exists(db_file)    # is it really useful anymore?
        self.db = sqlite3.connect(db_file)
        self.db_file = db_file    # is it really useful?
        
        # TODO: maybe is better to execute create_table method outside of object constructor?
        self.create_table(table)
    
    def read(self, command, values=None):
        '''
        Read content from database.
        '''
        self.cursor = self.db.cursor()
        if values is not None:
            self.cursor.execute(command, values)
        else:
            self.cursor.execute(command)
        # TODO: manage query with and without values
        # TODO: add cursor return
    
    def write(self, command, values=None):
        '''
        Write content to database.
        '''
        self.cursor = self.db.cursor()
        if values is not None:
            self.cursor.execute(command, values)
        else:
            self.cursor.execute(command)

        self.db.commit()
        # TODO: manage query with and without values
        # TODO: add cursor return
    
    def create_table(self, table):
        '''
        Create table.
        '''
        create_table_command = '''CREATE TABLE IF NOT EXISTS {tab} (
                                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                                username varchar NOT NULL,
                                asin varchar NOT NULL,
                                url varchar NOT NULL,
                                title varchar NOT NULL,
                                price float NOT NULL,
                                rating float,
                                last_check datetime NOT NULL,
                                is_deal bolean NOT NULL,
                                deal_expiry_time datetime,
                                price_diff float
                                );'''.format(tab=table)
        
        self.write(create_table_command)
    
    def drop_table(self, table):
        '''
        Delete table.
        '''
        drop_table_command = '''DROP TABLE {tab}'''.format(tab=table)
        
        self.write(drop_table_command)
    
    def check_table(self, table):
        '''
        Check table existence.
        '''
        check_table_command = '''SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{tab}"'''.format(tab=table)

        self.read(check_table_command)

        if self.cursor.fetchone()[0] == 1:
            return True
        else:
            return False
    
    def select(self, column, table, condition, product):    # TODO: rename product in values?
        '''
        Show row content.
        '''
        select_command = '''SELECT {col} FROM {tab} WHERE {cond} = ?'''.format(col=column, tab=table, cond=condition)

        if self.check_table(table) is True:
            self.read(select_command, product)    # TODO: rename product in values?

            return self.cursor.fetchall()
            # TODO: evaluate whether insert return of self.cursor.fetchall into read method

        else:
            pass
            # code to execute when table does not exists
    
    def select_all(self, table):
        '''
        Show all rows content.
        '''
        select_all_command = '''SELECT * FROM {tab}'''.format(tab=table)
        
        if self.check_table(table) is True:
            self.read(select_all_command)

            return self.cursor.fetchall()
            # TODO: evaluate whether insert return of self.cursor.fetchall into read method

        else:
            pass
            # code to execute when table does not exists
    
    def insert(self, table, product):    # TODO: rename product in values?
        '''
        Insert row into the table.
        '''
        insert_command = '''INSERT INTO {tab}(username,asin,url,title,
                            price,rating,last_check,is_deal,deal_expiry_time,
                            price_diff)
              VALUES(?,?,?,?,?,?,?,?,?,?)'''.format(tab=table)
        
        self.write(insert_command, product)    # TODO: rename product in values?

        return self.cursor.lastrowid
        # TODO: check what is returned (is it needed for variable assignment?)
    
    def update(self, column, condition, product):    # TODO: rename product in values?
        '''
        Update row content.
        '''
        update_command = '''UPDATE products SET {col} = ?
                            WHERE {cond} = ?'''.format(col=column, cond=condition)
        
        self.write(update_command, product)    # TODO: rename product in values?
        # TODO: return something (is it needed for variable assignment?)
    
    def delete(self, table, condition, product):    # TODO: rename product in values?
        '''
        Delete row.
        '''
        delete_command = '''DELETE FROM {tab} WHERE {cond} = ?'''.format(tab=table, cond=condition)
        
        self.write(delete_command, product)    # TODO: rename product in values?
        # TODO: return something (is it needed for variable assignment?)
    
    def delete_all(self, table):
        '''
        Delete all rows.
        '''
        delete_all_command = '''DELETE FROM {tab}'''.format(tab=table)

        self.write(delete_all_command)
        # TODO: return something (is it needed for variable assignment?)

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


def main():
    '''
    Main execution.
    '''
    # TODO: in the main execution function if asin already exists in the table then use update, else use insert

    pt = PriceTracker()
    page = pt.html("https://www.amazon.it/Rowenta-Smart-Force-Essential-Aspirapolvere/dp/B07BCNBZX8/ref=gbps_tit_s-5_1669_45c55016?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=9APEYZYZMMXHPN5SY7ZQ")
    url = "https://www.amazon.it/Rowenta-Smart-Force-Essential-Aspirapolvere/dp/B07BCNBZX8/ref=gbps_tit_s-5_1669_45c55016?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=9APEYZYZMMXHPN5SY7ZQ"

    obj = Product(url, pt.asin(url), pt.title(page), pt.price(page), pt.rating(page), pt.last_check(), pt.is_deal(page), pt.deal_expiry_time(page))
    obj.details()

    db = Database("pricetracker.sqlite3", "products")    # maybe will be useful to create a function for database initialization?

    product = ("dieguito84", obj.asin, obj.url, obj.title, obj.price, obj.rating, obj.last_check, obj.is_deal, obj.deal_expiry_time, "4")
    #db.insert("products", product)

    product_update = (obj.last_check, "4")
    #db.update("last_check", "id", product_update)

    product_delete = ("2")
    #db.delete("products", "id", product_delete)

    #db.delete_all("products")

    #db.drop_table("products")

    #db.commit()

    db.select_all("products")

    product_select = (obj.asin,)
    # added the comma to pass a tuple
    # otherwise I get sqlite3.ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1 error"
    db.select("id", "products", "asin", product_select)

    # test for price_diff method
    last_price_select = (obj.asin,)
    last_price = db.select("price", "products", "asin", last_price_select) 
    current_price = obj.price
    print("Il vecchio prezzo era {old_price}".format(old_price=last_price[0][0]))
    print("Il nuovo prezzo è {new_price}".format(new_price=current_price))
    print("La differenza di prezzo è {price_difference}".format(price_difference=pt.price_diff(url, page)))

    db.disconnect()

if __name__ == "__main__":
    main()