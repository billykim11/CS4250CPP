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
        db = client.cpppf
        print("---DB---")
        print(db)
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully")

def cleansing_list(input):
    # List of elements for remove...
    rm = ['Title:', 'Title', 'Office:', 'Office', 'Phone:', 'Phone', 'Email:', 'Email', 'Web:', 'Web', ':', ':']
    for x in range(0, len(rm)):
        try:
            input.remove(rm[x])
        except Exception as error:
            print('Skip Remove')

    return input

def save_html_information(db, pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web):
    try:
        ## Collection
        col = db.faculties
        if pf_name != '':
            doc = {
                "name": pf_name,
                "title": pf_title,
                "office": pf_office,
                "phone": pf_phone,
                "email": pf_email,
                "web": pf_web

            }
            result = col.insert_one(doc)
            print(result.inserted_id, ' has been Stored')
        else:
            print('SKIP Storing')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False

def get_target_page(db):
    try:
        ## Collection
        col = db.cspages
        ## Find Page
        pipeline = [
            {'$match': {'title': 'Permanent Faculty'}}
        ]
        ## Query
        docs = col.aggregate(pipeline)
        for data in docs:
            html_source = data['html']
            print(html_source)
        return html_source
    except Exception as error:
        print("Mongo DB Error")
        return None


## Initial Infos.
# target_page = ['https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml']
partial_url_starter = 'https://www.cpp.edu'

## Get DB Connection
db = connectDataBase()

try:
    ###html_page = urlopen(target_page[0])
    ## Get Html Content From DB
    html_page = get_target_page(db)
    print(html_page)
except HTTPError as e:
    print(e)
    # return null, break, or do some other "Plan B"
else:
    # program continues.
    my_soup = bs(html_page, "html.parser")
    all_prof = my_soup.find_all('div', {"class": "clearfix"})
    for prof in all_prof:
        pf_name = pf_title = pf_office = pf_phone = pf_email = pf_web = ''
        prof_name = prof.find_all('h2')
        for name in prof_name:
            ##print(name.get_text())
            pf_name = name.get_text().strip()
        ptag = prof.find_all('p')
        for p in ptag:
            ##print(p.get_text(strip=True, separator='\n').splitlines())
            info_list = p.get_text(strip=True, separator='\n').splitlines()
            clean_list = cleansing_list(info_list)
            pf_title = clean_list[0].replace(':','').strip()
            pf_office = clean_list[1].replace(':','').strip()
            pf_phone = clean_list[2].replace(':','').strip()
            pf_email = clean_list[3].replace(':','').strip()
            pf_web = partial_url_starter + clean_list[4].replace(':','').strip()
        print(pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web)
        db_result = save_html_information(db, pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web)
        print(db_result)
