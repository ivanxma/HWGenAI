import globalvar
import mysql.connector

# MySQL Connectoin Profile
myconfig = globalvar.myconfig

# Used to connect to MySQL
def connectMySQL(myconfig) :
    cnx = mysql.connector.connect(**myconfig)
    return cnx

def callProc(theProc, args, cnx) :

    dataset=[]
    columnset=[]
    try : 
       with cnx.cursor() as cursor:
         result_args = cursor.callproc(theProc, args)
         for result in cursor.stored_results():
           rows = result.fetchall()
           columns = result.column_names
           dataset.append(rows)
           columnset.append(columns)
    except Exception as error:
        print("Error calling SP", error)

    returnvar={}
    returnvar['output'] = result_args[1]
    returnvar['resultset'] = dataset
    returnvar['columnset'] = columnset
    return returnvar



def runSQL(theSQL, cnx ) :
    cursor = cnx.cursor()
    try : 
           cursor.execute(theSQL)
           data = cursor.fetchall()
           return data

    except mysql.connector.Error as error:
        print("executing SQL failure : {}".format(error))
    finally:
            if cnx.is_connected():
                cursor.close()

def getEmbModel() :
    cnx = connectMySQL(myconfig)
    embModels=[]
    try:
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='TEXT_EMBEDDINGS'
        """, cnx )
        for row in data:
           embModels.append(row[0])

    except Exception as error:
        embModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(embModels)

def getLLMModel() :
    cnx = connectMySQL(myconfig)
    llmModels=[]
    try:
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='GENERATION'
        """, cnx )
        for row in data:
           llmModels.append(row[0])

    except Exception as error:
        llmModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(llmModels)

def getVisionLLMModel() :
    cnx = connectMySQL(myconfig)
    llmModels=[]
    try:
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='GENERATION' and model_id like '%vision%'
        """, cnx)
        for row in data:
           llmModels.append(row[0])

    except Exception as error:
        llmModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(llmModels)

def getNLSQLLLMModel() :
    cnx = connectMySQL(myconfig)
    llmModels=[]
    try:
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='GENERATION' and model_id in ('meta.llama-3.3-70b-instruct', 'meta.llama-3.3-70b-instruct', 'llama3.1-8b-instruct-v1', 'llama3.2-3b-instruct-v1')
        """, cnx)
        for row in data:
           llmModels.append(row[0])

    except Exception as error:
        llmModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(llmModels)


def getDB() :
    cnx = connectMySQL(myconfig)
    mylist=[]
    try:
        data = runSQL("""
          select schema_name from information_schema.schemata 
        """, cnx)
        for row in data:
           mylist.append(row[0])

    except Exception as error:
        mylist=[]
        print("Error while inserting in DB : ", error)

    return tuple(mylist)
