# DB
import mysql.connector
import globalvar
from mysql.connector import errorcode

PRODUCTSQL = 'SELECT * from productdb.product where itemid = {}'

def connectMySQL(myconfig):
    cnx = mysql.connector.connect(**myconfig)
    return cnx

myconfig = globalvar.myconfig

def get_product_list():
    conn = connectMySQL(myconfig)
    c = conn.cursor(prepared=True)
    c.execute('SELECT * from productdb.product')
    data = {}
    data['colnames'] = c.column_names
    data['rows'] = c.fetchall()
    c.close()
    conn.close()
    return data

def get_generation_llms():
    conn = connectMySQL(myconfig)
    data = runSQL("SELECT model_id, provider FROM sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]' = 'GENERATION'", conn)
    conn.close()
    return data

def get_product_detail(itemid):
    conn = connectMySQL(myconfig)
    c = conn.cursor(prepared=True)
    print(PRODUCTSQL.format(itemid))
    c.execute(PRODUCTSQL.format(itemid))
    data = {}
    data['colnames'] = c.column_names
    data['rows'] = c.fetchall()
    c.close()
    conn.close()
    return data

def runSQL(theSQL, cnx) :
    cursor = cnx.cursor()
    try :
        cursor.execute(theSQL)
        data = {}
        data['colnames'] = cursor.column_names
        data['rows'] = cursor.fetchall()
        return data

    except mysql.connector.Error as error:
        print("executing SQL failure : {}".format(error))
        st.info("executing SQL error : {}".format(error))
    finally:
            if cnx.is_connected():
                cursor.close()


# OCI-LLM: Used to prompt the LLM
def query_llm_with_prompt( myconfig, myprompt, mytemplate, allm, aoptions, ml_generate_options):

    conn = connectMySQL(myconfig)
    cursor = conn.cursor()
      
    myoptions = ""
    for myitem in ml_generate_options :
      if myitem in aoptions :
        myoptions = myoptions + ', "' + myitem + '",' + str(aoptions[myitem])

    newprompt = myprompt.replace('"', "'")
    newtemplate = mytemplate.replace('"', "'")
    call_string = """
        select sys.ML_GENERATE("{query}", JSON_OBJECT("task", "generation", "model_id", "{myllm}" {options}, "context", "{template}") )
    """.format(query=newprompt,myllm=allm, options=myoptions, template=newtemplate)
    print(call_string)

    cursor.execute(call_string)
        
    data = cursor.fetchall()
    cursor.close()
    conn.close()
        
    return data[0][0]
