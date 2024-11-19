import mysql.connector
import mysql.connector as sqlctr
import sys
from datetime import datetime

mycon = sqlctr.connect(host='localhost', user='root', password='8123')
if mycon.is_connected():
    print('\nSuccessfully connected to localhost')
else:
    print('Error while connecting to localhost')

cursor = mycon.cursor()

cursor.execute("create database if not exists pathsala")
cursor.execute("use pathsala")

cursor.execute("create table if not exists books(SN int(5) primary key, Book_Name varchar(30), Quantity_Available int(10), Price_Per_Day int(10))")
cursor.execute("create table if not exists borrower(SN int(5), borrowers_name varchar(40), book_lent varchar(20), borrow_date date, contact_no int(10))")

def command(st, values=None):
    if values is None:
        cursor.execute(st)
    else:
        cursor.execute(st, values)

def fetch():
    data = cursor.fetchall()
    for i in data:
        print(i)

def all_data(tname):
    li = []
    st = 'desc '+tname
    command(st)
    data = cursor.fetchall()
    for i in data:
        li.append(i[0])
    st = 'select * from '+tname
    command(st)
    print('\n')
    print('-------ALL_DATA_FROM_TABLE_'+tname+'_ARE-------\n')
    print(tuple(li))
    fetch()

def detail_borrower(name,contact):
    tup=('SN','borrowers_name','book_lent','date','contact_no')
    print('\n---Details for borrower '+name+'---\n')
    print(tup)
    st='select * from BORROWER where borrowers_name like "{}" and contact_no={}'.format(name,contact)
    command(st)
    fetch()

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    global days
    days=abs((d2 - d1).days)

def price_book(days,book_name):
    st1 = 'select Price_Per_Day from books where Book_Name="{}"'.format(book_name)
    command(st1)
    data = cursor.fetchall()
    for i in data:
        global t_price
        t_price=int(i[0])*days
        print('No. of days {} book is kept : {}'.format(book_name,days))
        print('Price per day for book {} is Rs.{}'.format(book_name,i[0]))
        print('Total fare for book '+book_name +'-',t_price)

def book_list():
    st = 'SELECT * FROM books'
    command(st)
    data = cursor.fetchall()
    if len(data) == 0:
        print("No books available in the library.")
    else:
        print("Available Books in Library:")
        for i in data:
            print("Book ID:", i[0])
            print("Book Name:", i[1])
            print("Author Name:", i[2])
            print("Quantity Available:", i[3])
            print("\n")

def lend():
    book_list()  # Display available books

    print("\nTo lend a book, please provide the following details:")
    borrower_name = input("Enter Borrower's Name: ")
    book_lent = input("Enter Book Lent: ")
    borrowed_date = input("Enter Borrowed Date (YYYY-MM-DD): ")
    contact_no = input("Enter Contact Number: ")

    # Generate a unique serial number for each lending entry
    cursor.execute("SELECT MAX(SN) FROM borrower")
    result = cursor.fetchone()
    borrower_id = result[0] + 1 if result[0] else 1

    st_insert = "INSERT INTO borrower (SN, borrowers_name, book_lent, borrow_date, contact_no) VALUES (%s, %s, %s, %s, %s)"
    values = (borrower_id, borrower_name, book_lent, borrowed_date, contact_no)

    try:
        command(st_insert, values)
        print("Book Lending Entry added successfully!")
    except mysql.connector.Error as err:
        print("Error: Unable to add book lending entry.", err)

    main_menu()


def borrowers():
    print('\n\n__OPTIONS AVAILABLE__\n\nEnter 1 : To Show detail of all borrowers \nEnter 2 : To check detail of a particular borrower \nEnter 3 : To calculate total fine of a borrower \nEnter 4 : To go Back \nEnter 5 : To commit all the changes and exit')
    dec = input('enter your choice-')
    if dec=='1':
        all_data('borrower')
    elif dec=='2':
        name = str(input('\nenter borrower name-'))
        contact = str(input('enter borrower contact no.-'))
        detail_borrower(name,contact)
    elif dec=='3':
        tfine()
    elif dec=='4':
        main_menu()
    elif dec=='5':
        close()
    borrowers()

def tfine():
    name = str(input('\nEnter borrower name : '))
    contact = input('Enter borrower contact_no : ')
    detail_borrower(name, contact)
    st1 = 'select book_lent from borrower where borrowers_name ="{}" and contact_no={}'.format(name, contact)
    command(st1)
    data = cursor.fetchall()
    for i in data:
        book_name = i[0]
        st2 = 'select borrow_date from borrower where borrowers_name="{}" and book_lent="{}"'.format(name, book_name)
        command(st2)
        data1 = cursor.fetchall()
        for date in data1:
            date_taken = date[0]
            date_return = str(input('\nEnter returning date for book "{}" (YYYY-MM-DD), Press ENTER to skip - '.format(book_name)))
            while date_return != '':
                days_between(str(date_return), str(date_taken))
                price_book(days, i[0])
                print('\nEnter Y: If Rs.{} is paid and book is returned.\nEnter N: If fare is not paid and book is not returned.'.format(t_price))
                dec = str(input('Enter (Y/N): '))
                if dec.upper() == "Y":
                    st = 'select SN , Quantity_Available from books where Book_Name ="{}"'.format(i[0])
                    command(st)
                    data2 = cursor.fetchall()
                    for price in data2:
                        update('books', 'Quantity_Available', price[1] + 1, price[0])
                    st_del = 'delete from borrower where borrowers_name="{}" and book_lent="{}"'.format(name, book_name)
                    command(st_del)
                    break
                else:
                    print("\n\nPLEASE PAY THE FARE AND RETURN BOOK AFTER READING.\n\n")
                    break

def insert():
    flag = 'true'
    while flag == 'true':
        licol = []

        command('desc books')
        data = cursor.fetchall()
        for i in data:
            licol.append(i[0])

        # Fetch the maximum SN or default to 1 if no records are present
        command('select max(SN) from books')
        dta = cursor.fetchall()
        max_sn = dta[0][0]
        next_sn = (max_sn or 0) + 1

        li_val = [next_sn]

        for k in range(1, 4):
            val = str(input('Enter ' + licol[k] + '-'))
            li_val.append(val)

        placeholders = ', '.join(['%s'] * 4)  # Assuming there are 4 columns (SN, Book_Name, Quantity_Available, Price_Per_Day)
        columns = ', '.join(licol)  # Include all column names
        st1 = "INSERT INTO books ({}) VALUES ({})".format(columns, placeholders)

        command(st1, tuple(li_val))  # Include all values

        all_data('books')
        print("\nDATA INSERTED SUCCESSFULLY\n")

        dec = str(input('Do you want to insert more data? (Y/N) - '))
        if dec.upper() == "Y":
            flag = 'true'
        else:
            flag = 'false'

    main_menu()




def update(tname,col1,post_value,pre_value):
    st = str('update %s set %s=%s where SN=%s') % (tname, col1, "'%s'", "'%s'") % (post_value, pre_value)
    command(st)
    all_data(tname)
    print('\nVALUE UPDATED SUCCESSFULLY')
     
def close():
    close_connection()

def close_connection():
    mycon.commit()
    mycon.close()
    if mycon.is_connected():
        print('Still connected to localhost')
    else:
        print('\n\nConnection closed successfully.')
    sys.exit()

def main_menu():
    print('\n#### WELCOME TO LIBRARY MANAGEMENT SYSTEM ####')
    print('\nEnter 1 : To View details of all available Books')
    print('Enter 2 : To check detail of a particular book')
    print('Enter 3 : To lend a book')
    print('Enter 4 : To add new books in list')
    print('Enter 5 : To update data')
    print('Enter 6 : To view details of borrowers')
    print('Enter 7 : To commit all changes and exit')
    
    dec = input('\nEnter your choice: ')
    
    if dec == '1':
        all_data('books')
    elif dec=='2':
        tup=('SN','Book_Name','Quantity_Available','Price_Per_Day')
        tup1 = ('SN', 'borrowers_name', 'book_lent', 'contact_no')
        in1=str(input('enter first name , last name or middle name of a book-'))
        print('\n__ALL DATA OF BOOKS HAVING "{}" IN THEIR NAME FROM BOTH TABLE_'.format(in1))
        st =str('select * from books where book_name like "{}"'.format('%'+in1+'%'))
        st1=str('select * from borrower where book_lent like "{}"'.format('%'+in1+'%'))
        print('\n_DATA FROM TABLE BOOKS_\n')
        command(st)
        print(tup)
        fetch()
        print('\n_DATA FROM TABLE BORROWER_\n')
        command(st1)
        print(tup1)
        fetch()
        print()
    elif dec == '3':
        lend()
    elif dec == '4':
        insert()
    elif dec=='5':
        flag='true'
        while flag=='true':
            tname = 'books'
            li = []
            st1 = 'desc '+tname
            command(st1)
            data = cursor.fetchall()
            for i in data:
                li.append(i[0])
            all_data(tname)
            print('\n columns in table '+tname+' are')
            print(li)
            col1 = str(input('enter column name for modification from above list-'))
            lipo = ['SN']
            lipo.append(col1)
            print(tuple(lipo))
            st0 = 'select SN , %s from books' % (col1)
            command(st0)
            fetch()
            pre_value = str(input('enter corresponding SN for the data to be changed-'))
            post_value = str(input('enter new value for column %s having SN %s-' % (col1, pre_value)))
            update(tname, col1, post_value, pre_value)
            dec = str(input('Do you want to change more data?(Y/N)-'))
            if dec == 'y' or dec == 'Y':
                flag='true'            
            else:
                flag='false'
    elif dec == '6':
        borrowers()
    elif dec == '7':
        close()
    
    main_menu()

main_menu()
