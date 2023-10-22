#-------------------------------------------------------------------------
# AUTHOR: your name
# FILENAME: title of the source file
# SPECIFICATION: description of the program
# FOR: CS 4250- Assignment #2
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
# --> add your Python code here
import pprint

import pymongo
import sys, traceback
import datetime

def remove_punctuation(input):
    input = str(input).strip()
    char_remove = ['.','?','!',',',';',':','-','(',')','[',']','{','}','\'','"']
    for char in char_remove:
        input = input.replace(char, '')
    return input


def count_term(term_list, chk_term):
    count = 0
    for elem in term_list:
        if elem == chk_term:
            count += 1
    return count


def createTermList(docText_cleansing):
    found_terms = docText_cleansing.lower().split(' ')
    print(found_terms)

    # Convert the list to a set
    rm_set = set(found_terms)

    # Convert the set back to a list
    distinct_terms = list(rm_set)
    print(distinct_terms)

    term_list = []
    for term in distinct_terms:
        term_list.append({"term": str(term).lower(), "num_char": len(term), "num_term": count_term(found_terms, term)})

    print(term_list)
    return term_list


def connectDataBase():
    # Create a database connection object using pymongo
    # --> add your Python code here
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        print("---Client---")
        print(client)
        db = client.library
        print("---DB---")
        print(db)
        print("---Current DB List---")
        print(client.list_database_names())

        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully")


def createDocument(col, docId, docText, docTitle, docDate, docCat):
    print("Create Docs")
    print(docId, docText, docTitle, docDate, docCat)

    docText_cleansing = remove_punctuation(docText)
    numChar = len(docText_cleansing.replace(' ', ''))

    if docDate == '':
        create_date = datetime.datetime.now()
    else:
        create_date = datetime.datetime.strptime(docDate, "%Y-%m-%d")

    doc = {
        "doc_no": int(docId),
        "title": str(docTitle),
        "text": str(docText),
        "num_char": numChar,
        "created_at": create_date,
        "category": docCat,
        "terms": createTermList(docText_cleansing)
    }

    # create a dictionary to count how many times each term appears in the document.
    # Use space " " as the delimiter character for terms and remember to lowercase them.
    # --> see the method "createTermList"

    # create a list of dictionaries to include term objects.
    # --> see the method "createTermList"

    #Producing a final document as a dictionary including all the required document fields
    # --> see the method "createTermList"

    # Insert the document
    # --> add your Python code here
    result = col.insert_one(doc)
    print(result.inserted_id)
    print("Doc has been Created...")

def deleteDocument(col, docId):
    print("Delete Docs")
    # Delete the document from the database
    # --> add your Python code here
    find_doc = col.find_one({"doc_no": int(docId)})
    print(find_doc)
    _id = find_doc["_id"]
    print(_id)
    col.delete_one({"_id": _id})
    print("Doc Deleted...")

def updateDocument(col, docId, docText, docTitle, docDate, docCat):
    # Delete the document
    # --> add your Python code here
    print("Delete Docs")
    deleteDocument(col, docId)

    # Create the document with the same id
    # --> add your Python code here
    print("Recreate Docs")
    createDocument(col, docId, docText, docTitle, docDate, docCat)
    print("Doc Updated...")

def getIndex(col):
    print("Get Indexes")
    pipeline = [
        {
            '$unwind': {
                'path': '$terms'
            }
        }, {
            '$group': {
                '_id': [
                    '$title', '$terms.term'
                ],
                'cnt': {
                    '$sum': '$terms.num_term'
                }
            }
        }, {
            '$sort': {
                'terms.term': 1
            }
        }
    ]
    docs = col.aggregate(pipeline)
    print(docs)
    index_dict = {}
    tmp = ''
    for data in docs:
        title = data['_id'][0]
        term = data['_id'][1]
        num_term = data['cnt']
        if tmp != term:
            value_str = title+':'+str(num_term)
            tmp = term
        else:
            value_str += ', '+title + ':' + str(num_term)

        index_dict.update({term: value_str})

    return index_dict

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    # --> add your Python code here
