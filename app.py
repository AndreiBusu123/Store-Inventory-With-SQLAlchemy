from models import (Base, session, Product, engine)
import datetime
import csv

def convert_price_to_cents(price_str): # Converts price string to cents integer format for database storage
    try:
        price_without_dollar_sign = price_str.replace('$', '')
        price_float = float(price_without_dollar_sign)
        price_cents = int(price_float * 100)
        return price_cents
    except ValueError:
        print(f"Error converting price: {price_str}")
        return 0


def clean_product_name(name_str): # Cleans the product name by removing quotation marks and removes whitespace that could couse issues
    clean_name = name_str.replace('"', '').replace("'", '').strip()
    return clean_name


def clean_date(date_str): # converts the date string to a datetime object I need this for the database
    cleaned_date = datetime.datetime.strptime(date_str, '%m/%d/%Y').date()
    return cleaned_date


def deduplicate_products(product_data): # This one was a #@#$@%er for me to do and I needed some help.
    # Essentially this function will be used both for the initial csv import and also for adding products manually.
    # It checks if the product already exists in the database and updates it if the new data is more recent.
    # If the product does not exist, it adds it to the database.

    # Queries the DB to check if the product already exists
    existing_product = session.query(Product).filter_by(product_name = product_data['product_name']).first()
    # If it doesnt then it adds it under new_product 
    if not existing_product:
        new_product = Product(
            product_name=product_data['product_name'],
            product_price=product_data['product_price'],
            product_quantity=product_data['product_quantity'],
            date_updated=product_data['date_updated']
        )
        # And then commits the changes to the database session
        session.add(new_product)
        session.commit()
        return 'added'
    
    #If it does exist then this checks to make sure that the date_updated is more recent and commits if it is, otherwise just goes home and bakes a cake and forgets about the whole thing. 
    else:
        if product_data['date_updated'] > existing_product.date_updated:
            existing_product.product_price = product_data['product_price']
            existing_product.product_quantity = product_data['product_quantity']
            existing_product.date_updated = product_data['date_updated']
            session.commit()
            return 'updated' # This is more for the manual entry but essentially it will be used to determine my logic and print statements for the manual entry
        else:
            return 'skipped' # see above


def add_csv():
    # I had to use DictReader as it made it 1 million times easier as I could now use the column names as keys in the dictionary
    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)
        #this is where the magic happens and I loop through each row in the csv file, clean the data using the respective functions
        #and then call deduplicate_products which handles the add/update/skip logic 
        for row in data:
            clean_product = {
                'product_name': clean_product_name(row['product_name']),
                'product_price': convert_price_to_cents(row['product_price']),
                'product_quantity': int(row['product_quantity']),
                'date_updated': clean_date(row['date_updated'])
            }
            #What a sexy function this is. 
            deduplicate_products(clean_product) 


def view_product():
    #This bit is pretty easy really, I just query and print
    products = session.query(Product).all()
    for product in products:
        print(f"{product.product_id}: {product.product_name}, ")
    #Setting up the While loop 
    while True:
        selection = input("Which product would you like to view? [Enter product ID (example: 21) or 'e' to exit]: ")

        if selection.lower() == 'e':
            print("Exiting the product view.")
            return
        elif not selection.isdigit():
            print("Please enter a valid product ID or 'e' to exit.")
            continue
        else:
            selected_id = int(selection)
            found_product = session.query(Product).filter(Product.product_id == selected_id).first()
            #Prints all the shizzle McDrizzle out. 
            if found_product:
                print("\n------ Product Details ------")
                print(f"Product ID: {found_product.product_id}")
                print(f"Product Name: {found_product.product_name}")
                print(f"Product Quantity: {found_product.product_quantity}")
                print(f"Product Price: ${found_product.product_price / 100:.2f}")
                print(f"Date Updated: {found_product.date_updated.strftime('%m/%d/%Y')}")
                print("Returning to the main menu...")
                return
            else: #Just in case I fucked up
                print(f"No product found with ID {selected_id}. Please try again.")


def validate_name(name_str): # does the same as clean name with a few extra features but for the manual input entry, 
    #I could have use the clean_product_name function but this adds a few extra checks. Probably wrong but hey live and learn. 
    name=name_str.strip().replace('"', '').replace("'", '')
    if not name:
        return None, "Product name cannot be empty."
    if len(name) < 2:
        return None, "Product name must be at least 2 characters long."
    if len(name) > 50:
        return None, "Product name must be less than 50 characters."
    else:
        return name, None     


def validate_price(price_str): # Validates the price input , making sure its not less than 0, and not more than $10k
    try:
        price = int(price_str)
        if price <= 0: 
            return None, "Price must be a positive integer."
        elif price > 1000000:
            return None, "Price must be less than $10,000.00."
        else:
            return price, None       
    except ValueError:
        return None, "Invalid price format. Please enter a valid whole number without any $ or decimal points. (Example: $4.99 is written as 499)."       
 

def get_date_input(): #This is for the manual entry so that they can use today or put another date in. 

    while True:
        date_choice = input("Use today's date? (y/n): ").lower()
        
        if date_choice == 'y': #returns todays date as a date object (still wrapping my head around date objects)
            return datetime.datetime.now().date()
        
        elif date_choice == 'n':
            print("Enter the date:")
            
            # Get day
            while True:
                day_input = input("Day (1-31): ")
                if day_input.isdigit() and 1 <= int(day_input) <= 31:
                    day = int(day_input)
                    break
                else:
                    print("Please enter a valid day (1-31)")
            
            # Get month
            while True:
                month_input = input("Month (1-12): ")
                if month_input.isdigit() and 1 <= int(month_input) <= 12:
                    month = int(month_input)
                    break
                else:
                    print("Please enter a valid month (1-12)")
            
            # Get year
            while True:
                year_input = input("Year (e.g., 2025): ")
                if year_input.isdigit() and int(year_input) >= 2000:
                    year = int(year_input)
                    break
                else:
                    print("Please enter a valid year (2000 or later)")
            
            # Returs the date if its valid, otherwise prints an error and loops back to el starto magnifico
            try:
                custom_date = datetime.date(year, month, day)
                return custom_date
            except ValueError as e:
                print(f"Invalid date: {e}")
                print("Please try again.")
                continue
        
        else:
            print("Please enter 'y' for yes or 'n' for no")      



def add_product():
    #This function was a bitch to write as it is actually was the most complex for me
    # We add a product and have to do some checks 
    print("\n------ Add Product ------")

    while True: #Enter product name and validate
        name_input = input("Enter the product name: ")
        add_product_name, error = validate_name(name_input)
        if error:
            print(f"Error: {error}")
            continue
        else:
            break

    while True: #Enter price and validate
        price_input = input("Enter the product price in cents (e.g., $10.99 is written as 1099):  ")
        add_product_price, error = validate_price(price_input)
        if error:
            print(f"Error: {error}")
            continue
        else:
            break

    while True: #Enter quantity and validate 
        quantity_input = input("Enter the product quantity: ")
        if not quantity_input.isdigit() or int(quantity_input) < 0:
            print("Please enter a valid non-negative whole number")
            continue
        else: 
            add_product_quantity = int(quantity_input)
            break

    # Use that beautiful function we made before 
    product_date = get_date_input()

    # Create product data dictionary
    new_product = {
        'product_name': add_product_name,
        'product_price': add_product_price,
        'product_quantity': add_product_quantity,
        'date_updated': product_date 
    }
    
    # Use deduplicate_products for consistency
    result = deduplicate_products(new_product)
    
    if result == 'added':
        print(f"Product '{add_product_name}' added successfully.")
    elif result == 'updated':
        print(f" Product '{add_product_name}' updated successfully.")
    else:
        print(f" Product '{add_product_name}' SKIPPED due to older date than existing product.\n Please check the dates and try again.")


def backup_database(): 
    # this creates a backup of the database, essentially running the add_csv in reverrse 
    print("Creating database backup")
    
    try:
        products = session.query(Product).all()
        
        #This shouldnt trigger but I put it in there just in case 
        if not products:
            print("Error: No products found in the database. Nothing to backup.")
            return
        
        #I had to get some help with this one, I tried using the csv module but had issues regarding the headers etc. 
        with open('backup.csv', 'w', newline='') as csvfile:
            fieldnames = ['product_name', 'product_price', 'product_quantity', 'date_updated']
            
            #creates the headers
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            #fills in the rows to the headers
            for product in products:
                writer.writerow({
                    'product_name': product.product_name,
                    'product_price': f"${product.product_price / 100:.2f}",
                    'product_quantity': product.product_quantity,
                    'date_updated': product.date_updated.strftime('%m/%d/%Y')
                })
        #prints confirmation message
        print(f"Database backup successful! {len(products)} products saved to 'backup.csv'")
        
    except Exception as e:
        print(f"Error creating backup: {e}")
    

def menu(): #This is just a standard menu, continues to loop until the user exits
    while True:
        main_menu_selection = input('''
                                    \n-------INVENTORY MANAGEMENT SYSTEM-------
                                    \rView Product (v)
                                    \rAdd Product (a)
                                    \rBackup Database (b)
                                    \rExit (e)
                                    \rPlease select an option (v, a, b, or e): ''')
        if main_menu_selection.lower() == 'v':
            view_product()
            continue
            
        elif main_menu_selection.lower() == 'a':
            add_product()
            continue
        elif main_menu_selection.lower() == 'b':
            backup_database()
            continue
        elif main_menu_selection.lower() == 'e':
            print("Exiting the program.")
            exit()
            break
        else:
            print("Please select a valid option (v, a, b, or e) from the menu and try again.")
            continue

if __name__ == "__main__":
    # creates the database tables, runs the add_csv function and then goes to menu. 
    Base.metadata.create_all(engine)
    add_csv()
    menu()