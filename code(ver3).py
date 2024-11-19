import mysql.connector as sqlctr
import sys

# Connect to the MySQL database
try:
    mycon = sqlctr.connect(host='localhost', user='root', password='root')
    if mycon.is_connected():
        print('Successfully connected to localhost')
    else:
        print('Error while connecting to localhost')
except Exception as e:
    print(f"Error: {e}")
    sys.exit()

cursor = mycon.cursor()

# Create database and use it
cursor.execute("CREATE DATABASE IF NOT EXISTS pathsala")
cursor.execute("USE pathsala")

# Create necessary tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        SN INT(5) PRIMARY KEY,
        Book_Name VARCHAR(30),
        Quantity_Available INT(10),
        Price_Per_Day INT(10)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS BORROWER (
        SN INT(5),
        borrowers_name VARCHAR(40),
        book_lent VARCHAR(20),
        contact_no varchar(13)
    )
""")

# Function to execute SQL commands
def command(st, params=None):
    cursor.execute(st, params) if params else cursor.execute(st)

# Function to fetch and print all data
def fetch():
    data = cursor.fetchall()
    for row in data:
        print(row)

# Function to show all data from a table
def all_data(tname):
    print(f"\n------- ALL DATA FROM TABLE {tname} -------\n")
    command(f"DESCRIBE {tname}")
    columns = cursor.fetchall()
    print("Columns:", [col[0] for col in columns])
    
    command(f"SELECT * FROM {tname}")
    fetch()

# Function to get details of a borrower
def detail_borrower(name, contact):
    print(f"\n--- Details for borrower {name} ---")
    command("SELECT * FROM BORROWER WHERE borrowers_name = %s AND contact_no = %s", (name, contact))
    fetch()

# Function to lend a book
def lend():
    while True:
        print('\n__AVAILABLE BOOKS__\n')
        command("SELECT Book_Name FROM books WHERE Quantity_Available >= 1")
        fetch()

        book_selected = input('Enter the name of the book to lend: ')
        borrowers_name = input('Enter Borrower Name: ')
        contact = input('Enter contact no.: ')
        
        # Insert borrower data
        command("""
            INSERT INTO BORROWER (SN, borrowers_name, book_lent, contact_no)
            SELECT IFNULL(MAX(SN), 0) + 1, %s, %s, %s FROM BORROWER
        """, (borrowers_name, book_selected, contact))

        # Update book quantity
        command("""
            UPDATE books SET Quantity_Available = Quantity_Available - 1 
            WHERE Book_Name = %s
        """, (book_selected,))
        
        # Ask if more records need to be added
        more_records = input('Do you want to lend another book (Y/N)? ').upper()
        if more_records != 'Y':
            break

# Function to calculate price for a book (without date logic)
def price_book(book_name):
    command('SELECT Price_Per_Day FROM books WHERE Book_Name = %s', (book_name,))
    price_per_day = cursor.fetchone()[0]
    print(f'Price per day for book "{book_name}" is Rs.{price_per_day}')
    return price_per_day

# Function to insert new books into the system
def insert():
    while True:
        book_name = input('Enter Book Name: ')
        quantity = int(input('Enter Quantity Available: '))
        price_per_day = int(input('Enter Price Per Day: '))

        command("""
            INSERT INTO books (SN, Book_Name, Quantity_Available, Price_Per_Day)
            SELECT IFNULL(MAX(SN), 0) + 1, %s, %s, %s FROM books
        """, (book_name, quantity, price_per_day))

        print(f"\nBook '{book_name}' added successfully.")
        
        more_books = input('Do you want to add more books (Y/N)? ').upper()
        if more_books != 'Y':
            break

# Function to update book data
def update():
    while True:
        column = input('Enter column name to update (Book_Name, Quantity_Available, Price_Per_Day): ').strip()
        if column not in ['Book_Name', 'Quantity_Available', 'Price_Per_Day']:
            print('Invalid column name. Please try again.')
            continue

        sn = int(input('Enter SN of the book to update: '))
        new_value = input(f'Enter new value for {column}: ')

        if column == 'Quantity_Available' or column == 'Price_Per_Day':
            new_value = int(new_value)  # Convert to integer for these fields

        command(f"UPDATE books SET {column} = %s WHERE SN = %s", (new_value, sn))
        print(f"Book with SN {sn} updated successfully.")

        more_updates = input('Do you want to update more books (Y/N)? ').upper()
        if more_updates != 'Y':
            break

# Function to close the connection
def close():
    mycon.commit()
    mycon.close()
    if mycon.is_connected():
        print('Still connected to localhost')
    else:
        print('\nConnection closed successfully.')
    sys.exit()

# Main menu system
def action_list():
    while True:
        print('\n#### WELCOME TO LIBRARY MANAGEMENT SYSTEM ####')
        print('1: View details of all available Books')
        print('2: View details of a particular book')
        print('3: Lend a book')
        print('4: Add new books to the list')
        print('5: Update book data')
        print('6: View borrower details')
        print('7: Commit changes and exit')
        
        choice = input('Enter your choice: ')
        
        if choice == '1':
            all_data('books')
        elif choice == '2':
            book_name = input('Enter part of the book name to search for: ')
            command('SELECT * FROM books WHERE Book_Name LIKE %s', ('%' + book_name + '%',))
            fetch()
        elif choice == '3':
            lend()
        elif choice == '4':
            insert()
        elif choice == '5':
            update()
        elif choice == '6':
            name = input('Enter borrower name: ')
            contact = int(input('Enter borrower contact number: '))
            detail_borrower(name, contact)
        elif choice == '7':
            close()
        else:
            print('Invalid choice. Please try again.')

# Start the application
action_list()
