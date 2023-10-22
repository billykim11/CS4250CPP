#-------------------------------------------------------------------------
# AUTHOR: your name
# FILENAME: title of the source file
# SPECIFICATION: description of the program
# FOR: CS 4250- Assignment #2
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#importing some Python libraries
from db_connection_solution import *

if __name__ == '__main__':

    # Connecting to the database
    conn = connectDataBase()
    print(conn)

    # Getting a cursor
    cur = conn.cursor()
    print(cur)

    #print a menu
    print("")
    print("######### Menu ##############")
    print("#a - Create a category.")
    print("#b - Create a document")
    print("#c - Update a document")
    print("#d - Delete a document.")
    print("#e - Output the inverted index.")
    print("#q - Quit")

    option = ""
    while option != "q":

          print("")
          option = input("Enter a menu choice: ")

          if (option == "a"):

              catId = input("Enter the ID of the category: ")
              catName = input("Enter the name of the category: ")

              result = createCategory(cur, catId, catName)
              if result:
                conn.commit()
              else:
                conn.rollback()

          elif (option == "b"):

              docId = input("Enter the ID of the document: ")
              docText = input("Enter the text of the document: ")
              docTitle = input("Enter the title of the document: ")
              docDate = input("Enter the date of the document: ")
              docCat = input("Enter the category of the document: ")

              result = createDocument(cur, docId, docText, docTitle, docDate, docCat)
              if result:
                conn.commit()
              else:
                conn.rollback()

          elif (option == "c"):

              docId = input("Enter the ID of the document: ")
              docText = input("Enter the text of the document: ")
              docTitle = input("Enter the title of the document: ")
              docDate = input("Enter the date of the document: ")
              docCat = input("Enter the category of the document: ")

              result = updateDocument(cur, docId, docText, docTitle, docDate, docCat)
              if result:
                conn.commit()
              else:
                conn.rollback()

          elif (option == "d"):

              docId = input("Enter the document id to be deleted: ")

              result = deleteDocument(cur, docId)
              if result:
                conn.commit()
              else:
                conn.rollback()

          elif (option == "e"):

              index = getIndex(cur)
              print(index)

          elif (option == "q"):

               print("Leaving the application ... ")

          else:

               print("Invalid Choice.")
