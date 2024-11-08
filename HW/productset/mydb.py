# DB
import mysql.connector
import globalvar

def connectMySQL(myconfig):
    cnx = mysql.connector.connect(**myconfig)
    return cnx

myconfig = globalvar.myconfig



# Functions
def view_all_products():
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('SELECT product_id, product_name, product_description, price FROM productdb.products limit 100')
	data = c.fetchall()
	c.close()
	conn.close()
	return data

def get_similar_products(question):
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('call productdb.get_similar_product_list("{}")'.format(question))
	data = c.fetchall()
	c.close()
	conn.close()
	return data

