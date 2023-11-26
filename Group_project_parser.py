from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import sys, traceback
import datetime

## functions
def connectDataBase():
    # Create a database connection object using pymongo
    # --> add your Python code here
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        print("---Client---")
        print(client)
        db = client.cs4250prj
        print("---DB---")
        print(db)
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully")

def get_faculty_info_from_db(db):
    ## Collection
    col = db.pages
    docs = col.find()
    for data in docs:
        fac_name = data['name']
        fac_title = data['title']
        fac_phone = data['phone']
        fac_office = data['office']
        fac_email = data['email']
        fac_web = data['web']
        # print(fac_name, fac_title, fac_phone, fac_office, fac_email, fac_web, )
        scrap_faculty_individual_page(db, fac_name, fac_title, fac_phone, fac_office, fac_email, fac_web)

def scrap_faculty_individual_page(db, param_name, param_title, param_phone, param_office, param_email, web):
    try:
        html_page = urlopen(web)
    except HTTPError as e:
        print(e)
        # return null, break, or do some other "Plan B"
        return None
    else:
        # program continues.
        my_soup = bs(html_page.read(), "html.parser")
        # print(my_soup)

        schedule_area = my_soup.find_all('span', {"class": "odd"})
        for schedule in schedule_area:
            print(schedule.text)
            param_schedule = schedule.text

        search_area = my_soup.find_all('div', {"id": "main-body"})
        # print(search_area)
        for search in search_area:
            content_area = search.find_all('div', {"class": "blurb"})
            for content in content_area:
                print('==========')
                h2 = content.find('h2')
                if h2:
                    print('~~~~~')
                    print(h2.text)
                    if h2.text == 'About Me':
                        param_category = 'About'
                    elif h2.text == 'Selected Publications':
                        param_category = 'Publications'
                    else:
                        param_category = 'Other'

                ps = content.find_all('p')
                print('~~~~~')
                param_content = ''
                for p in ps:
                    print(p.text)
                    param_content = p.text

                param_list = []
                ul = content.find('ul')
                if ul:
                    lis = ul.find_all('li')
                    print('~~~~~')
                    for li in lis:
                        print(li.text)
                        param_list.append(li.text)

                save_document_information(db, param_name, param_title, param_phone, param_office, param_email, param_schedule, param_category, param_content, param_list)
        return True

def save_document_information(db, pg_name, pg_title, pg_office, pg_phone, pg_email, pg_schedule, pg_category, pg_content, pg_list):
    try:
        ## Collection
        col = db.documents
        if pg_category == 'About' or pg_category == 'Publications':
            doc = {
                "name": pg_name,
                "title": pg_title,
                "phone": pg_phone,
                "office": pg_office,
                "email": pg_email,
                "odd": pg_schedule,
                "category": pg_category,
                "content": pg_content,
                "publication": pg_list
            }
            result = col.insert_one(doc)
            print(result.inserted_id, ' has been Stored')
        else:
            print('SKIP Storing')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False


### MongoDB Document Design
'''
document = {
    "_id": {},
    "doc_no": "[Integer Digit]",
    "author": "[String Professor's Name]",
    "title": "[String Professor's Title]",
    "email": "[String Professor's Email]",
    "office": "[String Professor's Office Number]",
    "phone": "[String Professor's Telephone Number]",
    "lecture": "[String Days of Lecture and Time]",
    "catetory": "['AboutMe' or 'SelectedPublication']",
}
'''


## Initial Infos.
partial_url_starter = 'https://www.cpp.edu'

## Get DB Connection
db = connectDataBase()

try:
    ## Get Html Content From DB
    get_faculty_info_from_db(db)
    # print(html_page)
except Exception as error:
    # program error
    traceback.print_exc()
    print("Database not connected successfully")
else:
    # program continue
    print("Continue")
