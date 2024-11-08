# DB
import mysql.connector
import globalvar

def connectMySQL(myconfig):
    cnx = mysql.connector.connect(**myconfig)
    return cnx

myconfig = globalvar.myconfig



# Functions
def create_table():
	conn = connectMySQL(myconfig)
	c = conn.cursor()
	c.execute('create table if not exists myreview (asin varchar(20), review_text text, title varchar(256), rating decimal(5,2), user_id varchar(30), review_timestamp timestamp, parent_asin varchar(20), helpful_vote decimal(5,2), verified_purchase varchar(10))')
	conn.commit()
	c.close();
	conn.close()


create_table()


def add_data(user_id, asin, title, review_text, postdate):
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('INSERT INTO reviewdb.myreview(asin,user_id, title,review_text,review_timestamp) VALUES (?,?,?,?,?)',(asin, user_id,title,review_text,postdate))
	c.close()
	conn.commit()
	conn.close()

def view_all_notes():
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('SELECT asin, user_id, title, review_text, rating, review_timestamp FROM reviewdb.myreview limit 10')
	data = c.fetchall()
	c.close()
	conn.close()
	return data

def view_all_titles():
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('SELECT DISTINCT title FROM reviewdb.myreview limit 20')
	data = c.fetchall()
	c.close()
	conn.close()
	return data


def get_review_by_title(title):
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('SELECT asin, user_id, title, review_timestamp, review_text, rating FROM reviewdb.myreview WHERE title="{}" limit 10'.format(title))
	data = c.fetchall()
	c.close()
	conn.close()
	return data

def get_review_by_user_id(user_id):
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('SELECT asin, user_id, title, review_timestamp, review_text, rating FROM reviewdb.myreview WHERE user_id="{}" limit 10'.format(user_id))
	data = c.fetchall()
	c.close()
	conn.close()
	return data

def delete_data(title):
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('DELETE FROM reviewdb.myreview WHERE title="{}" limit 10'.format(title))

	conn.commit()
	c.close()
	conn.close()

def get_review_summary_by_title(title,lang):
	conn = connectMySQL(myconfig)
	c = conn.cursor(prepared=True)
	c.execute('call SUMMARIZE_TRANSLATE("{}", "{}")'.format(title, lang) )
	data = c.fetchall()
	myout = ''
	if len(data) > 0:
		myx = data[0][0]
		myout = str(myx, encoding='utf-8')
	c.close()
	conn.close()
	mystr = str(myout)
	mystr = mystr.replace('\\n', '<br>')
	mystr = mystr.replace('\\', '')
	mystr = mystr.replace('"', '')
	return mystr.strip()
