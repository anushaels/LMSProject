#Faith Online Library System

import mysql.connector
from mysql.connector import Error
import re #for regular expressions in validations
from datetime import datetime, timedelta #for date-time calculations
import bcrypt #for password hashing


# Admin credentials are predefined
ADMIN_USERID = 'admin'
ADMIN_PASSWORD = 'admin@12'

#function to connect to database
def db_connect():
    return mysql.connector.connect(
        host='localhost',

        user='root',
        password='faith', #mysql password
        database='LMSDB2' #created a database 'LMSDB2' in the mysql
    )

#tables are created inside the lmsdbb1 database
def create_tables():
    table_creation_statements = [
        #table for the customer to signup with their details: Register is created if not exist
        '''
        CREATE TABLE IF NOT EXISTS register ( 
        id INT AUTO_INCREMENT PRIMARY KEY,
        firstname VARCHAR(50),
        lastname VARCHAR(50),
        number VARCHAR(15),
        mailid VARCHAR(50),
        userid VARCHAR(50) UNIQUE,
        password VARCHAR(50)
        )
        ''',
        #the details of books are stored in the books table
        '''
        CREATE TABLE IF NOT EXISTS Books (
            bookid INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            author VARCHAR(100),
            genre VARCHAR(50),
            rent_rate VARCHAR(10),
            status VARCHAR(20),
            startdate DATE,
            enddate DATE
        )
        ''',
        #Table for genre details
        '''
        CREATE TABLE IF NOT EXISTS genre (
            genre_id INT AUTO_INCREMENT PRIMARY KEY,
            genre_name VARCHAR(50),
            book_name VARCHAR(100)
        )
        ''',
        #predefined table for authors details
        '''
        CREATE TABLE IF NOT EXISTS author (
            author_id INT AUTO_INCREMENT PRIMARY KEY,
            author_name VARCHAR(50),
            authbook_name VARCHAR(50)
        )
        ''',
        #table for storing the details of plan each users selected with userid as fk
        '''
        CREATE TABLE IF NOT EXISTS SubscriptionPlan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            userid VARCHAR(50),
            plan VARCHAR(50),
            amount VARCHAR(10),
            payment_method VARCHAR(50),
            payment_details VARCHAR(100),
            status VARCHAR(20),
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (userid) REFERENCES register(userid)
        )
        ''',
        #The details of books rented by users are stored in rent_book table using bookid as fk
        '''
        CREATE TABLE IF NOT EXISTS rent_book (
            rent_id INT AUTO_INCREMENT PRIMARY KEY,
            bookid INT NOT NULL,
            userid varchar(50),
            title VARCHAR(255),
            author VARCHAR(255),
            genre VARCHAR(100),
            price VARCHAR(10),
            startdate DATE,
            enddate DATE,
            FOREIGN KEY (bookid) REFERENCES Books(bookid)
        )
        '''
    ]

    try:
        # For db connection
        conn = db_connect()
        cursor = conn.cursor()

        # Execute each table creation statement separately
        for statement in table_creation_statements:
            cursor.execute(statement)

        # Commit changes
        conn.commit()
        print("Tables created successfully")

    # telling the error when an error occurs
    except Error as e:
        print(f"Error: {e}")

    #if no err:
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print('MySQL connection successfull')

#function for Admin to login with the predefined userid and password
def admin_login():
    userid = input("Enter admin userid: ")
    password = input("Enter admin password: ")

    #checks if the admin inputed the same userid ans pass as the predefined userid and password
    if userid == ADMIN_USERID and password == ADMIN_PASSWORD:
        print("Login successful")
        admin_page()
    else:
        print("Invalid credentials or not an admin")


#admin dashboard is displayed using admin_page() function
def admin_page():
    while True:
        print("\n----Admin Page----")
        print("1. Add Book")
        print("2. View Book Details")
        print("3. View User Details")
        print("4. View Overdue Books")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_book()
        elif choice == '2':
            view_books()
        elif choice == '3':
            view_users()
        elif choice == '4':
            overdue_book()
        elif choice == '5':
            print("Exiting...\nThankyou for using the system....")
            break
        else:
            print("Invalid choice")

#Function for adding books by the admin
def add_book():
    name = input("Enter book name: ")
    author = input("Enter book author: ")

    print("Select genre:")
    print("1. Romance")
    print("2. Horror")
    print("3. Comic")
    print("4. Research")

    genre_choice = input("Enter the number corresponding to the genre: ")

    genre_map = {
        '1': 'Romance',
        '2': 'Horror',
        '3': 'Comic',
        '4': 'Research'
    }
    #retrieves the genre data according to the user
    genre = genre_map.get(genre_choice, 'Unknown')

    rent_rate = input("Enter rent rate: ")
    print("Choose the status of book")
    print("1. Available")
    print("2. UnAvailable")
    status_choice = input("Enter the number corresponding to the book status: ")

    status_map = {
        '1': 'Available',
        '2': 'UnAvailable'
    }
    #retrieves status of books on users choice
    status = status_map.get(status_choice, 'Unknown')

    # Get rental dates
    startdate = input("Enter rental start date (YYYY-MM-DD): ")
    enddate = input("Enter rental end date (YYYY-MM-DD): ")

    conn = db_connect()
    cursor = conn.cursor()

    #query to insert values to books table
    query = '''
    INSERT INTO Books (name, author, genre, rent_rate, status, startdate, enddate)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (name, author, genre, rent_rate, status, startdate, enddate))

    conn.commit() #commit the changes
    print("Book added successfully")

    cursor.close()
    conn.close() #closed connections

#function for admin to view the books in the system
def view_books():
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()

    for book in books:
        print(book)

    cursor.close()
    conn.close()

#function to view the users
def view_users():
    while True:
        print("\n--- View User Details ---")
        print("1. Subscribed Users")
        print("2. Unsubscribed Users")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_subscribed_users()
        elif choice == '2':
            view_unsubscribed_users()
        elif choice == '3':
            print("Exiting View User Details...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

#function in admin page to view the names of subscribed users
def view_subscribed_users():
    conn = db_connect()
    cursor = conn.cursor()

    try:
        # Query to get details of subscribed users using inner join
        query = '''
        SELECT r.firstname, r.lastname, r.mailid, r.number
        FROM register r
        JOIN SubscriptionPlan sp ON r.userid = sp.userid
        WHERE sp.status = 'Active'
        '''
        cursor.execute(query)
        users = cursor.fetchall()

        print("\n--- Subscribed Users ---")
        if users:
            for user in users:
                print(f"First Name: {user[0]}, Last Name: {user[1]}, Email ID: {user[2]}, Number: {user[3]}")
        else:
            print("No subscribed users found.")

    except Error as e:
        print(f"Error fetching subscribed users: {e}")

    cursor.close()
    conn.close()

#function in admin page to view the names of unsubscribed users
def view_unsubscribed_users():
    conn = db_connect()
    cursor = conn.cursor()

    try:
        #get details of unsubscribed users by left join on sp with register
        query = '''
        SELECT r.firstname, r.lastname, r.mailid, r.number
        FROM register r
        LEFT JOIN SubscriptionPlan sp ON r.userid = sp.userid
        WHERE sp.userid IS NULL OR sp.status = 'Expired'
        '''
        cursor.execute(query)
        users = cursor.fetchall()

        print("\n--- Unsubscribed Users ---")
        if users:
            for user in users:
                print(f"First Name: {user[0]}, Last Name: {user[1]}, Email ID: {user[2]}, Number: {user[3]}")
        else:
            print("No unsubscribed users found.")

    except Error as e:
        print(f"Error fetching unsubscribed users: {e}")

    cursor.close()
    conn.close()

#function in admin page to view the list of overdue books
def overdue_book():
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)  # Use dictionary=True for better readability

    # Get current date
    current_date = datetime.now().date()

    try:
        # get details of overdue books by using inner join on bookss with rent_books
        query = """
            SELECT rb.rent_id, rb.bookid, b.name, rb.startdate, rb.enddate
            FROM rent_book rb
            JOIN Books b ON rb.bookid = b.bookid
            WHERE rb.enddate < %s
        """

        cursor.execute(query, (current_date,))
        overdue_books = cursor.fetchall()

        if not overdue_books:
            print("No overdue books found.")
        else:
            print("Overdue Books:")
            for book in overdue_books:
                print(f"Rent ID: {book['rent_id']}, Book ID: {book['bookid']}, Title: {book['name']}, Start Date: {book['startdate']}, End Date: {book['enddate']}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

#the main menu of customer dashboard to login or signup
def customer_menu():
    while True:
        print("\n-----------------------------------")
        print("1. Login")
        print("2. New user?Signup..")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            logincus()
        elif choice == '2':
            customer_register()
        elif choice == '3':
            print("System exiting...")
            break
        else:
            print("Invalid choice! Choose up to 3 only")

#function for customer to signup with their details
def customer_register():
    conn = db_connect()
    cursor = conn.cursor()

    while True:
        try:
            print("Sign up with your details here.")
            first_name = input("Enter the first name: ")
            last_name = input("Enter the last name: ")

            while True:
                number = input("Enter the number(starts with 6,7,8,9 and should be 10 digits): ")
                if re.fullmatch(r'^[6-9]\d{9}$', number):
                    break
                else:
                    print("Invalid! Number should contain 10 digits and start with 6, 7, 8, or 9")

            while True:
                email = input("Enter the email id(example@gmail.com): ")
                if re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    break
                else:
                    print("Invalid! Please enter a valid email address")

            while True:
                userid = input("Create a user ID(alphanumeric,6-12characters): ")
                if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,12}$', userid):
                    break
                else:
                    print("INVALID! User ID should be alphanumeric and 6-12 characters long.")

            while True:
                password = input("Enter the password(6-12 alphnnumeric char with atleast 1 spl & uppercase characters): ")
                if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+!_])[A-Za-z\d@#$%^&+!_]{6,12}$',
                                password):
                    break
                else:
                    print(
                        "INVALID! Password must be 6-12 characters long with 1 uppercase, 1 lowercase, 1 digit, and 1 special character.")

            #query to insert values to the register table
            insert_query = "INSERT INTO register (firstname, lastname, number, mailid, userid, password) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (first_name, last_name, number, email, userid, password))
            conn.commit()

            print("You are signed up successfully...Now login..")
            return

        except Error as e:
            print(f"Error: {e}")
            conn.rollback()

    cursor.close()
    conn.close()

#function for customers to login with their username &password
def logincus():
    conn = db_connect()
    cursor = conn.cursor()

    print("Enter your details here")
    userid = input("Enter the user id: ")
    password = input("Enter password: ")

    # check whether the username and password matches to that in db
    try:
        query = "SELECT * FROM register WHERE userid = %s AND password = %s"
        cursor.execute(query, (userid, password))
        result = cursor.fetchone()

        if result:
            print(f"Welcome, {userid}!")
            customer_page()

        else:
            print("Invalid login credentials")

    except Error as e:
        print(f"Error: {e}")

    cursor.close()
    conn.close()

#Customer dashboard is displayed using customer_page
def customer_page():
    # user_id = view_plan()
    while True:
        print("\n----------Welcome User----------")
        print("Select one from below..")
        print("1. Genre")
        print("2. Author")
        print("3. Choose Plan")
        print("4. View Plan")
        print("5. Rent book")
        print("6. Logout")

        choice = input("enter the choice: ")
        if choice == '1':
            genre()
        elif choice == '2':
            Author()
        elif choice == '3':
            choose_plan()
        elif choice == '4':
            view_plan()
        elif choice == '5':
            choose_rent()
        elif choice == '6':
            print("You are logging out....Thankyou for using this app..")
            break
        else:
            print("Invalid choice")

#function to view the books according to their genre
def genre():
    # Establish database connection
    conn = db_connect()
    cursor = conn.cursor()

    while True:
        print("\n---------- Genre List -----------")
        print("1. Romance")
        print("2. Horror")
        print("3. Comic")
        print("4. Research")
        print("5. Exit")

        genre_choice = input("Enter the choice of genre you want to view or '5' to exit: ")

        # Genre map
        genre_map = {
            '1': 'Romance',
            '2': 'Horror',
            '3': 'Comic',
            '4': 'Research'
        }

        # Exit option
        if genre_choice == '5':
            print("Exiting Genre Menu...")
            break

        # retrieve genre based on user's input
        genre = genre_map.get(genre_choice)

        if genre:
            try:
                # Query to select books from the selected genre
                query = "SELECT name, author, rent_rate, status FROM Books WHERE genre = %s"
                cursor.execute(query, (genre,))
                books = cursor.fetchall()

                # Display books of the selected genre
                print(f"\nBooks in {genre} genre:")
                if books:
                    for book in books:
                        print(f"Name: {book[0]}, Author: {book[1]}, Rent Rate: Rs{book[2]}, Status: {book[3]}")
                else:
                    print(f"No books found in the {genre} genre.")
            except Error as e:
                print(f"Error fetching books: {e}")
        else:
            print("Invalid genre choice. Please select a valid option.")

    # Close the cursor and connection
    cursor.close()
    conn.close()

#function to view the list of authors
def Author():
    conn = db_connect()
    cursor = conn.cursor()

    while True:
        print("\n---------- Author List -----------")
        print("1. View Authors")
        print("2. Exit")

        choice = input("Enter your choice or '2' to exit: ")

        if choice == '2':
            print("Exiting Author Menu...")
            break

        if choice == '1':
            try:
                # Query to select all authors from the author table
                query = "SELECT author_id, author_name, authbook_name FROM author"
                cursor.execute(query) #execute the query
                authors = cursor.fetchall()

                # Display authors
                print("\nList of Authors:")
                if authors:
                    for author in authors:
                        print(f"Author ID: {author[0]}, Author Name: {author[1]}, Book Name: {author[2]}")
                else:
                    print("No authors found.")
            except Error as e:
                print(f"Error fetching authors: {e}")

    cursor.close()
    conn.close() #connection closed

#validation for Gpay
def validate_gpay_id(gpay_id):
    # Example validation: GPay ID should be a valid email address
    return re.match(r"^[0-9A-Za-z]{2,256}@[A-Za-z]{2,64}$", gpay_id)

#validation for acnt no
def validate_account_number(account_number):
    # Bank account number should be numeric and 12 digits
    return re.match(r"^\d{12}$", account_number)

#validation for credit card details(card number,expiry date,cvc)
def validate_credit_card_details(card_number, expiry_date, cvc):
    # cc number should be 12 digits, expiry date (MM/YY), and CVC (3 digits)
    card_valid = re.match(r"^\d{12}$", card_number)
    expiry_valid = re.match(r"^(0[1-9]|1[0-2])\/([0-9]{2})$", expiry_date)
    cvc_valid = re.match(r"^\d{3}$", cvc)
    return card_valid and expiry_valid and cvc_valid

#function for the customer to choose the plan from the 3 plans
def choose_plan():
    conn = db_connect()
    cursor = conn.cursor()

    plans = {
        '1': ('6 month plan', '500'),
        '2': ('1 year plan', '1000'),
        '3': ('2 year plan', '1500')
    }

    while True:
        print("\n------- Choose Plan ---------")
        print("1. 6 month plan - Rs 500")
        print("2. 1 year plan - Rs 1000")
        print("3. 2 year plan - Rs 1500")
        print("4. Exit")

        plan_choice = input("Enter the choice of plan: ")

        if plan_choice == '4':
            break

        plan = plans.get(plan_choice)
        if not plan:
            print("Invalid choice! Please choose a valid plan.")
            continue

        plan_name, amount = plan
        payment_method = input("Enter your payment method (Credit Card, Bank Transfer, GPay): ").lower()

        payment_details = None

        # each payemnt options in if condition
        if payment_method == 'gpay':
            while True:
                gpay_id = input("Enter your GPay ID(example@bank): ")
                if validate_gpay_id(gpay_id):
                    payment_details = gpay_id
                    break
                else:
                    print("Invalid GPay ID. Please enter a valid UPI ID (example@okaxisbank) address.")

        elif payment_method == 'bank transfer':
            while True:
                account_number = input("Enter your Bank Account Number(should be 12 digits): ")
                if validate_account_number(account_number):
                    payment_details = account_number
                    break
                else:
                    print("Invalid account number. Please enter a numeric account number with 12 digits.")

        elif payment_method == 'credit card':
            while True:
                credit_card_number = input("Enter your Credit Card Number(should be 12digits): ")
                expiry_date = input("Enter Expiry Date (MM/YY): ")
                cvc = input("Enter CVC(should be 3 digits): ")

                if validate_credit_card_details(credit_card_number, expiry_date, cvc):
                    payment_details = f"Card: {credit_card_number}, Expiry: {expiry_date}, CVC: {cvc}"
                    break
                else:
                    print("Invalid credit card details. Please check the card number should be 12 digits, expiry date, and CVC should be 3 digits only.")

        else:
            print("Invalid payment method! Please choose either Credit Card, Bank Transfer, or GPay.")
            continue

        # manage rental books dates
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=(180 if plan_choice == '1' else 365 if plan_choice == '2' else 730))

        status = 'Active'

        try:
            # Assuming you have the `userid` stored somewhere from the login session
            userid = input("Enter your User ID: ")

            #user's values are inserted to SubscriptionPlan table
            insert_query = '''
            INSERT INTO SubscriptionPlan (userid, plan, amount, payment_method, payment_details, status, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (userid, plan_name, amount, payment_method, payment_details, status, start_date, end_date))
            conn.commit()

            print(f"Plan '{plan_name}' selected successfully!")
            print(f"Subscription is valid until {end_date}")

        except Error as e:
            print(f"Error subscribing to plan: {e}")
            conn.rollback()

    cursor.close()
    conn.close()

#function to view the selected plans of the user according to his userid
def view_plan():
    conn = db_connect()
    cursor = conn.cursor()

    userid = input("Enter your User ID to view your plan: ")  # Replace this with actual user session ID

    try:
        # Query to get the user's active subscription plan details using inner join
        query = '''
        SELECT r.firstname, r.lastname, sp.plan, sp.amount, sp.payment_method, sp.start_date, sp.end_date, sp.status
        FROM register r
        JOIN SubscriptionPlan sp ON r.userid = sp.userid
        WHERE r.userid = %s AND sp.status = 'Active'
        '''
        cursor.execute(query, (userid,))
        subscription = cursor.fetchone()

        if subscription:
            print("\n--- Your Subscription Plan ---")
            print(f"First Name: {subscription[0]}")
            print(f"Last Name: {subscription[1]}")
            print(f"Plan: {subscription[2]}")
            print(f"Amount: Rs {subscription[3]}")
            print(f"Payment Method: {subscription[4]}")
            print(f"Start Date: {subscription[5]}")
            print(f"End Date: {subscription[6]}")
            print(f"Status: {subscription[7]}")
        else:
            print("No active subscription found for this user.")

    except Error as e:
        print(f"Error: {e}")

    cursor.close()
    conn.close()

#function that allow customer to rent the book only after he have subscribed to a plan
def choose_rent():
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)

    try:
        userid = input("Enter your User ID: ")

        # Check if the user has an active subscription
        check_subscription_query = """
        SELECT * FROM SubscriptionPlan 
        WHERE userid = %s AND status = 'Active'
        AND CURDATE() BETWEEN start_date AND end_date
        """
        cursor.execute(check_subscription_query, (userid,))
        active_subscription = cursor.fetchone()

        #if the user don't have a plan he will asked to choose a plan and then he can rent the book after the plan is subscribed
        if active_subscription is None:
            print("You don't have an active subscription plan. Please subscribe to a plan to rent a book.")
            return

        # Ask for the book name
        book_name = input("Enter the name of the book you want to rent: ")

        # Query to get book details by name
        query = "SELECT * FROM Books WHERE name = %s"
        cursor.execute(query, (book_name,))
        book = cursor.fetchone()

        if book is None:
            print("No book found with that name.")
            return

        # Check if the book is available,
        if book['status'] != 'Available':
            # displays when the book is unavailable
            print("The book is not available at the moment. Please choose another book.")
            return

        # If the book is available, proceed with renting the book
        bookid = book['bookid']

        # Insert values to rent_book table
        rent_query = """
        INSERT INTO rent_book (bookid, title, author, genre, price, startdate, enddate, userid) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(rent_query, (bookid, book_name, book['author'], book['genre'], book['rent_rate'], book['startdate'], book['enddate'], userid))
        conn.commit()

        print("Congratulations! You've rented the book! Happy reading!")

        # Display the list of books rented by the user
        rented_books_query = """
        SELECT * FROM rent_book
        WHERE userid = %s
        """
        cursor.execute(rented_books_query, (userid,))
        rented_books = cursor.fetchall()

        print("\nList of books you have rented:")
        for rented_book in rented_books:
            print(f"Book ID: {rented_book['bookid']}, Title: {rented_book['title']}, Author: {rented_book['author']}, Genre: {rented_book['genre']}, Price: {rented_book['price']}, Start Date: {rented_book['startdate']}, End Date: {rented_book['enddate']}")

    except Error as e:
        print(f"Error: {e}") #tells which error have occured
    finally:
        cursor.close()
        conn.close()

#ensuring that the main menu is displayed first
if __name__ == "__main__":
    create_tables()
    while True:
        print("\n--------Welcome to Faith Online Library-------")
        print("1. Admin Login")
        print("2. Customer Login")
        print("3. Exit")

        main_choice = input("Enter your choice: ")

        if main_choice == '1':
            admin_login()
        elif main_choice == '2':
            customer_menu()
        elif main_choice == '3':
            print("Exiting...\nThankyou for using this system..:)\nSee you Soon")
            break
        else:
            print("Invalid choice! Please select up to 3 options")
