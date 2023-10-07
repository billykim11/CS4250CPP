#-------------------------------------------------------------------------
# AUTHOR: your name
# FILENAME: title of the source file
# SPECIFICATION: description of the program
# FOR: CS 4250- Assignment #1
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

from datetime import datetime

# importing some Python libraries
import psycopg2
from psycopg2.extras import RealDictCursor


def remove_punctuation(input):
    input = str(input).strip()
    char_remove = ['.','?','!',',',';',':','-','(',')','[',']','{','}','\'','"']
    for char in char_remove:
        input = input.replace(char, '')
    return input

####################################################################################
def connectDataBase():

    # Create a database connection object using psycopg2
    DB_NAME = "CS4250CPP"
    DB_USER = "postgres"
    DB_PASS = "Capella@3288"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT,
                                cursor_factory=RealDictCursor)
        return conn

    except:

        print("Database not connected successfully")


def createCategory(cur, catId, catName):

    # Check Category ID is already exist or Not.
    cur.execute("select id from public.category where id = %s", (catId, ))
    result = cur.fetchone()
    if result:
        print('Category ID cannot be duplicated... please try another one.')
    else:
        # Insert a category in the database
        sql = "Insert into public.category (id, cat_name) Values (%s, %s)"
        recset = [catId, catName]
        cur.execute(sql, recset)


def createDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Get the category id based on the informed category name
    cur.execute("select id from public.category where cat_name = %s", (docCat,))
    result = cur.fetchone()
    if result:
        idCat = result['id']
    else:
        print('Category not Exist. Please check Again.')
        return False

    # 2 Insert the document in the database. For num_chars, discard the spaces and punctuation marks.
    sql = "Insert into public.document (document_no, doc_text, num_char, title, created_at, category_id) Values (%s, %s, %s, %s, %s, %s)"

    docText_cleansing = remove_punctuation(docText)
    numChar = len(docText_cleansing.replace(' ', ''))

    created_at = datetime.strptime(docDate, '%Y-%m-%d')

    recset = [docId, docText, numChar, docTitle, created_at, idCat]
    cur.execute(sql, recset)

    # 3 Update the potential new terms.
    # 3.1 Find all terms that belong to the document. Use space " " as the delimiter character for terms and Remember to lowercase terms and remove punctuation marks.
    # 3.2 For each term identified, check if the term already exists in the database
    # 3.3 In case the term does not exist, insert it into the database
    found_terms = docText_cleansing.split(' ')
    print(found_terms)
    for term in found_terms:
        cur.execute("select id from public.term where term = %s", (term,))
        result = cur.fetchone()
        if not result:
            cur.execute("Insert into public.term (term, num_char) Values (%s, %s)", [str(term).lower(), len(term)])

    # 4 Update the index
    # 4.1 Find all terms that belong to the document
    # 4.2 Create a data structure the stores how many times (count) each term appears in the document
    # 4.3 Insert the term and its corresponding count into the database
    cur.execute("select id, term from public.term where id > %s", (0,))
    results = cur.fetchall()
    for rlt in results:
        term_count = docText_cleansing.lower().count(str(rlt['term']).lower())
        if term_count > 0:
            cur.execute("Insert into public.indexdocument (document_no, term_id, num_term) Values (%s, %s, %s)", [docId, rlt['id'], term_count])

    return True

def deleteDocument(cur, docId):

    # 1 Query the index based on the document to identify terms
    # 1.1 For each term identified, delete its occurrences in the index for that document
    # 1.2 Check if there are no more occurrences of the term in another document. If this happens, delete the term from the database.
    sql = "Delete from public.indexdocument where document_no = %(id)s"
    cur.execute(sql, {'id': docId})

    cur.execute("Select id, term from public.term where id > %s", (0,))
    results = cur.fetchall()
    for rlt in results:
        cur.execute("Select count(term_id) as cnt from public.indexdocument where term_id = %s", (rlt['id'],))
        result = cur.fetchone()
        if int(result['cnt']) == 0:
            sql = "Delete from public.term where id = %(id)s"
            cur.execute(sql, {'id': rlt['id']})

    # 2 Delete the document from the database
    sql = "Delete from public.document where document_no = %(id)s"
    cur.execute(sql, {'id': docId})

    return True

def updateDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Delete the document
    deleteDocument(cur, docId)

    # 2 Create the document with the same id
    createDocument(cur, docId, docText, docTitle, docDate, docCat)

    return True

def getIndex(cur):

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    cur.execute(""" SELECT T.term, D.title, I.num_term 
                    FROM public.term T
                    INNER JOIN public.indexdocument I
                        ON T.id = I.term_id 
                    INNER JOIN public."document" D
                        ON I.document_no = D.document_no 
                    ORDER BY T.term """)

    index_dict = {}
    value_str = ''
    tmp = ''
    results = cur.fetchall()
    for rlt in results:
        if tmp != rlt['term']:
            value_str = rlt['title']+':'+str(rlt['num_term'])
            tmp = rlt['term']
        else:
            value_str += ', '+rlt['title'] + ':' + str(rlt['num_term'])

        index_dict.update({rlt['term']: value_str})

    return index_dict
