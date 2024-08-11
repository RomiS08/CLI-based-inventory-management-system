import sqlite3 # SQLite database module
import pandas as pd # Data manipulation and analysis library
from reportlab.lib.pagesizes import letter # Page size for PDF
from reportlab.pdfgen import canvas # Library to create PDF documents


# Class to represent a bike
class Bike:
    def __init__(self, make, model, quantity, price):
        self.make = make
        self.model = model
        self.quantity = quantity
        self.price = price

# Class to handle inventory operations
class Inventory:
    def __init__(self, db_name="inventory.db"):
        # Connect to SQLite database
        self.conn = sqlite3.connect(db_name)
        # Create table if it doesn't exist
        self.create_table()

    def create_table(self):
        # SQL to create a table for bikes
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bikes (
                id INTEGER PRIMARY KEY,
                make TEXT,
                model TEXT,
                quantity INTEGER,
                price REAL
            )
        ''')
        self.conn.commit()

    def add_bike(self, make, model, quantity, price):
        # Add a new bike to the database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO bikes (make, model, quantity, price)
            VALUES (?, ?, ?, ?)
        ''', (make, model, quantity, price))
        self.conn.commit()

    def search_price(self, make, model):
        # Search for the price of a bike by make and model
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT price FROM bikes WHERE make = ? AND model = ?
        ''', (make, model))
        result = cursor.fetchone()
        return result[0] if result else None

    def create_invoice(self, make, model, quantity):
        # Create an invoice for selling a bike
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, quantity, price FROM bikes WHERE make = ? AND model = ?
        ''', (make, model))
        result = cursor.fetchone()
        if result:
            bike_id, available_quantity, price = result
            if available_quantity >= quantity:
                # Update the quantity in the inventory
                new_quantity = available_quantity - quantity
                cursor.execute('''
                    UPDATE bikes SET quantity = ? WHERE id = ?
                ''', (new_quantity, bike_id))
                self.conn.commit()
                total_price = quantity * price
                return f"Invoice:\nMake: {make}\nModel: {model}\nQuantity: {quantity}\nTotal Price: {total_price}"
            else:
                return "Insufficient Stock."
        else:
            return "Bike Not Found. Please Check Details or Contact Sales."

    def display_inventory(self):
        # Display the current inventory
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT make, model, quantity, price FROM bikes
        ''')
        bikes = cursor.fetchall()
        report = "Inventory Report:\n"
        for bike in bikes:
            report += f"Make: {bike[0]}, Model: {bike[1]}, Quantity: {bike[2]}, Price: {bike[3]}\n"
        return report

    def generate_excel_report(self, file_name="inventory_report.xlsx"):
        cursor = self.conn.cursor()
        # Generate an Excel report of the inventory
        cursor.execute('''
            SELECT make, model, quantity, price FROM bikes
        ''')
        bikes = cursor.fetchall()
        df = pd.DataFrame(bikes, columns=["Make", "Model", "Quantity", "Price"])
        df.to_excel(file_name, index=False)

    def generate_pdf_report(self, file_name="inventory_report.pdf"):
        # Generate a PDF report of the inventory
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT make, model, quantity, price FROM bikes
        ''')
        bikes = cursor.fetchall()
        c = canvas.Canvas(file_name, pagesize=letter)
        c.drawString(100, 750, "Inventory Report")
        y = 720
        for bike in bikes:
            c.drawString(100, y, f"Make: {bike[0]}, Model: {bike[1]}, Quantity: {bike[2]}, Price: {bike[3]}")
            y -= 20
        c.save()

#----------------------  Main function to run the CLI menu -------------------

def main():
    inventory = Inventory()  # ------------- Create an Inventory object

    while True:
        # Display the menu
        print("\n         >>>>> Madhumal Motors Inventory System <<<<<    ")
        print("       -------------------------------------------------  \n")
        print("1. Add Bike")
        print("2. Search Price")
        print("3. Create Invoice")
        print("4. Display Inventory")
        print("5. Generate Excel Report")
        print("6. Generate PDF Report")
        print("7. Exit")

        choice = input(" \n Enter your choice: ")

        if choice == '1':
            # Add a new bike to the inventory
            make = input("Enter Bike make: ")
            model = input("Enter Bike model: ")
            quantity = int(input("Enter Quantity: "))
            price = float(input("Enter Price(LKR): "))
            inventory.add_bike(make, model, quantity, price)
            print("Bike Added Successfully.")

        elif choice == '2':
            # Search for the price of a bike
            make = input("Enter bike make: ")
            model = input("Enter bike model: ")
            price = inventory.search_price(make, model)
            if price is not None:
                print(f"The price of {make} {model} is {price}.")
            else:
                print("Bike not found.")

        elif choice == '3':
            # Create an invoice for selling a bike
            make = input("Enter bike make: ")
            model = input("Enter bike model: ")
            quantity = int(input("Enter quantity: "))
            invoice = inventory.create_invoice(make, model, quantity)
            print(invoice)

        elif choice == '4':
            # Display the current inventory
            report = inventory.display_inventory()
            print(report)

        elif choice == '5':
            # Generate an Excel report of the inventory
            file_name = input("Enter Excel file name (default: inventory_report.xlsx): ") or "inventory_report.xlsx"
            inventory.generate_excel_report(file_name)
            print(f"Excel report generated: {file_name}")

        elif choice == '6':
            # Generate a PDF report of the inventory
            file_name = input("Enter PDF file name (default: inventory_report.pdf): ") or "inventory_report.pdf"
            inventory.generate_pdf_report(file_name)
            print(f"PDF report generated: {file_name}")

        elif choice == '7':
            # Exit the program
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

# Run the main function if this script is executed

if __name__ == "__main__":
    main()
