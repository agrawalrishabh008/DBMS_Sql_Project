import tkinter as tk
from tkinter import simpledialog, messagebox
import mysql.connector as mc
import random

class InventoryManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")

        self.db_password = simpledialog.askstring("Password", "Enter your MySQL password:", show='*')
        self.db_connection = mc.connect(host="localhost", user="root", password=self.db_password, database="test1")
        self.cur = self.db_connection.cursor()

        self.main_menu()

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_widgets()
        menu_options = [
            ("View All Products", self.view_all_products),
            ("Add a Product", lambda: self.add_or_modify_product(is_new=True)),
            ("Modify a Product", lambda: self.add_or_modify_product(is_new=False)),
            ("Fetch Product Details", self.fetch_product_details),
            ("Delete a Product", self.delete_product),
            ("View Supplier Data", self.view_supplier_data),
            ("Remove Supplier", self.remove_supplier),
            ("Manage Transactions", self.manage_transactions),
            ("Quit", self.exit_app)
        ]

        for text, command in menu_options:
            tk.Button(self.root, text=text, command=command).pack(pady=2)

    def manage_transactions(self):
        self.clear_widgets()
        transaction_options = [
            ("View Transactions", self.view_transactions),
            ("Add a Transaction", self.add_transaction),
            ("Modify a Transaction", self.modify_transaction),
            ("Fetch Transaction Details", self.fetch_transaction_details),
            ("Delete a Transaction", self.delete_transaction),
            ("Back to Main Menu", self.main_menu)
        ]

        for text, command in transaction_options:
            tk.Button(self.root, text=text, command=command).pack(pady=2)

    # Product Management
    def view_all_products(self):
        self.cur.execute("SELECT * FROM Products")
        products = self.cur.fetchall()
        message = "\n".join([f"ID: {p[0]}, Name: {p[1]}, Supplier: {p[2]}, CP: {p[3]}, SP: {p[4]}, Inventory: {p[5]}" for p in products])
        messagebox.showinfo("All Products", message if message else "No products found.")

    def add_or_modify_product(self, is_new):
        product_id = simpledialog.askstring("Product ID", "Enter Product ID:")
        if not product_id:
            return
        if not is_new:
            self.cur.execute("SELECT * FROM Products WHERE PRODUCT_ID = %s", (product_id,))
            if not self.cur.fetchone():
                messagebox.showerror("Error", "Product not found.")
                return
        name = simpledialog.askstring("Product Name", "Enter Product Name:")
        supplier = simpledialog.askstring("Supplier", "Enter Supplier Name:")
        cost_price = simpledialog.askinteger("Cost Price", "Enter Cost Price:", minvalue=0)
        selling_price = simpledialog.askinteger("Selling Price", "Enter Selling Price:", minvalue=0)
        inventory = simpledialog.askinteger("Inventory", "Enter Inventory Amount:", minvalue=0)

        if is_new:
            query = "INSERT INTO Products (PRODUCT_ID, PRODUCT_NAME, SUPPLIER, COST_PRICE, SELLING_PRICE, INVENTORY) VALUES (%s, %s, %s, %s, %s, %s)"
        else:
            query = "UPDATE Products SET PRODUCT_NAME = %s, SUPPLIER = %s, COST_PRICE = %s, SELLING_PRICE = %s, INVENTORY = %s WHERE PRODUCT_ID = %s"

        self.cur.execute(query, (name, supplier, cost_price, selling_price, inventory, product_id) if not is_new else (product_id, name, supplier, cost_price, selling_price, inventory))
        self.db_connection.commit()
        messagebox.showinfo("Success", "Product added successfully." if is_new else "Product modified successfully.")

    def fetch_product_details(self):
        product_id = simpledialog.askstring("Fetch Product", "Enter Product ID:")
        self.cur.execute("SELECT * FROM Products WHERE PRODUCT_ID = %s", (product_id,))
        product = self.cur.fetchone()
        if product:
            details = f"ID: {product[0]}, Name: {product[1]}, Supplier: {product[2]}, CP: {product[3]}, SP: {product[4]}, Inventory: {product[5]}"
            messagebox.showinfo("Product Details", details)
        else:
            messagebox.showerror("Error", "Product not found.")

    def delete_product(self):
        product_id = simpledialog.askstring("Delete Product", "Enter Product ID to delete:")
        self.cur.execute("DELETE FROM Products WHERE PRODUCT_ID = %s", (product_id,))
        self.db_connection.commit()
        messagebox.showinfo("Success", "Product deleted successfully.")

    # Supplier Management
    def view_supplier_data(self):
        supplier_name = simpledialog.askstring("Supplier Name", "Enter Supplier Name:")
        self.cur.execute("SELECT * FROM Products WHERE SUPPLIER = %s", (supplier_name,))
        products = self.cur.fetchall()
        if products:
            message = "\n".join([f"ID: {p[0]}, Name: {p[1]}, Inventory: {p[5]}" for p in products])
            messagebox.showinfo("Supplier Products", message)
        else:
            messagebox.showinfo("Supplier Products", "No products found for this supplier.")

    def remove_supplier(self):
        supplier_name = simpledialog.askstring("Remove Supplier", "Enter Supplier Name to remove:")
        self.cur.execute("DELETE FROM Products WHERE SUPPLIER = %s", (supplier_name,))
        self.db_connection.commit()
        messagebox.showinfo("Success", "Supplier removed successfully.")

    # Transaction Management
    def view_transactions(self):
        self.cur.execute("SELECT * FROM Transactions")
        transactions = self.cur.fetchall()
        if transactions:
            message = "\n".join(
                [f"ID: {t[0]}, Day: {t[1]}, Quantity: {t[2]}, Sales: {t[3]}, Profit: {t[4]}, Loss: {t[5]}" for t in
                 transactions])
            messagebox.showinfo("All Transactions", message)
        else:
            messagebox.showinfo("All Transactions", "No transactions found.")

    def add_transaction(self):
        day = simpledialog.askstring("Add Transaction", "Enter Day (e.g., Monday):")
        quantity = simpledialog.askinteger("Add Transaction", "Enter Quantity:", minvalue=0)
        sales = simpledialog.askinteger("Add Transaction", "Enter Sales:", minvalue=0)
        profit = simpledialog.askinteger("Add Transaction", "Enter Profit:", minvalue=0)
        loss = simpledialog.askinteger("Add Transaction", "Enter Loss:", minvalue=0)
        if day and quantity is not None and sales is not None and profit is not None and loss is not None:
            self.cur.execute(
                "INSERT INTO Transactions (Day, Quantity, Sales, Profit, Loss) VALUES (%s, %s, %s, %s, %s)",
                (day, quantity, sales, profit, loss))
            self.db_connection.commit()
            messagebox.showinfo("Success", "Transaction added successfully.")
        else:
            messagebox.showerror("Error", "Transaction not added. Please fill all fields correctly.")

    def modify_transaction(self):
        transaction_id = simpledialog.askinteger("Modify Transaction", "Enter Transaction ID:")
        new_day = simpledialog.askstring("Modify Transaction", "Enter new Day (e.g., Monday):")
        new_quantity = simpledialog.askinteger("Modify Transaction", "Enter new Quantity:", minvalue=0)
        # Repeat for sales, profit, and loss as needed
        if transaction_id and new_day and new_quantity is not None:
            self.cur.execute("UPDATE Transactions SET Day = %s, Quantity = %s WHERE TransactionID = %s",
                             (new_day, new_quantity, transaction_id))
            self.db_connection.commit()
            messagebox.showinfo("Success", "Transaction modified successfully.")
        else:
            messagebox.showerror("Error", "Modification failed. Ensure you've entered valid data.")

    def fetch_transaction_details(self):
        transaction_id = simpledialog.askinteger("Fetch Transaction", "Enter Transaction ID:")
        self.cur.execute("SELECT * FROM Transactions WHERE TransactionID = %s", (transaction_id,))
        transaction = self.cur.fetchone()
        if transaction:
            details = f"ID: {transaction[0]}, Day: {transaction[1]}, Quantity: {transaction[2]}, Sales: {transaction[3]}, Profit: {transaction[4]}, Loss: {transaction[5]}"
            messagebox.showinfo("Transaction Details", details)
        else:
            messagebox.showerror("Error", "Transaction not found.")

    def delete_transaction(self):
        transaction_id = simpledialog.askinteger("Delete Transaction", "Enter Transaction ID:")
        self.cur.execute("DELETE FROM Transactions WHERE TransactionID = %s", (transaction_id,))
        self.db_connection.commit()
        messagebox.showinfo("Success", "Transaction deleted successfully.")

    def exit_app(self):
        self.db_connection.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagementApp(root)
    root.mainloop()
