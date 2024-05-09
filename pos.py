import tkinter as tk
from tkinter import messagebox
import sqlite3

class ProductManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Manager")

        self.db_conn = sqlite3.connect("products.db")
        self.db_cursor = self.db_conn.cursor()
        self.create_table()

        # Configure button colors
        self.add_color = "red"  # dull yellow
        self.sell_color = "green"  # green
        self.transaction_color = "orange"  # red

        self.add_button = tk.Button(root, text="Add Product", command=self.add_product, bg=self.add_color)
        self.add_button.pack(fill="x", pady=5)

        self.sell_button = tk.Button(root, text="Sell Product", command=self.sell_product, bg=self.sell_color)
        self.sell_button.pack(fill="x", pady=5)

        self.transaction_button = tk.Button(root, text="Transactions", command=self.show_transactions, bg=self.transaction_color)
        self.transaction_button.pack(fill="x", pady=5)

        # Center the buttons vertically
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def create_table(self):
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT,
                                    price REAL,
                                    quantity INTEGER
                                )''')

        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT,
                                    price REAL,
                                    quantity INTEGER,
                                    total_cost REAL,
                                    type TEXT
                                )''')
        self.db_conn.commit()

    def add_product(self):
        self.add_window = tk.Toplevel()
        self.add_window.title("Add Product")

        tk.Label(self.add_window, text="Name:").grid(row=0, column=0)
        tk.Label(self.add_window, text="Price:").grid(row=1, column=0)
        tk.Label(self.add_window, text="Quantity:").grid(row=2, column=0)

        self.name_entry = tk.Entry(self.add_window)
        self.name_entry.grid(row=0, column=1)
        self.price_entry = tk.Entry(self.add_window)
        self.price_entry.grid(row=1, column=1)
        self.quantity_entry = tk.Entry(self.add_window)
        self.quantity_entry.grid(row=2, column=1)

        self.submit_button = tk.Button(self.add_window, text="Submit", command=self.submit_product, bg=self.add_color)
        self.submit_button.grid(row=3, columnspan=2)

    def submit_product(self):
        name = self.name_entry.get()
        price = float(self.price_entry.get())
        quantity = int(self.quantity_entry.get())

        existing_product = self.db_cursor.execute("SELECT * FROM products WHERE name=?", (name,)).fetchone()

        if existing_product:
            new_quantity = existing_product[3] + quantity
            self.db_cursor.execute("UPDATE products SET quantity=? WHERE name=?", (new_quantity, name))
        else:
            self.db_cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))

        self.db_conn.commit()

        total_cost = price * quantity
        self.db_cursor.execute("INSERT INTO transactions (name, price, quantity, total_cost, type) VALUES (?, ?, ?, ?, ?)",
                               (name, price, quantity, total_cost, "add"))
        self.db_conn.commit()
        self.add_window.destroy()

    def sell_product(self):
        self.sell_window = tk.Toplevel()
        self.sell_window.title("Sell Product")

        self.refresh_product_list()  # Update product list

        if not self.product_names:
            messagebox.showerror("Error", "No products available for sale.")
            return

        tk.Label(self.sell_window, text="Select Product:").grid(row=0, column=0)
        self.product_var = tk.StringVar(value=self.product_names[0])
        self.product_dropdown = tk.OptionMenu(self.sell_window, self.product_var, *self.product_names)
        self.product_dropdown.grid(row=0, column=1)

        tk.Label(self.sell_window, text="Quantity:").grid(row=1, column=0)
        self.quantity_entry = tk.Entry(self.sell_window)
        self.quantity_entry.grid(row=1, column=1)

        self.sell_button = tk.Button(self.sell_window, text="Sell", command=self.process_sell, bg=self.sell_color)
        self.sell_button.grid(row=2, columnspan=2)

    def refresh_product_list(self):
        products = self.db_cursor.execute("SELECT name, quantity FROM products").fetchall()
        self.product_names = [row[0] for row in products if row[1] > 0]

    def process_sell(self):
        product_name = self.product_var.get()
        quantity = int(self.quantity_entry.get())

        product_info = self.db_cursor.execute("SELECT * FROM products WHERE name=?", (product_name,)).fetchone()

        if product_info:
            if product_info[3] >= quantity:
                total_cost = product_info[2] * quantity
                self.db_cursor.execute("UPDATE products SET quantity=quantity-? WHERE name=?", (quantity, product_name))
                self.db_cursor.execute("INSERT INTO transactions (name, price, quantity, total_cost, type) VALUES (?, ?, ?, ?, ?)",
                                    (product_name, product_info[2], quantity, total_cost, "sell"))
                self.db_conn.commit()
                messagebox.showinfo("Success", f"Product sold successfully for ${total_cost}")
                self.sell_window.destroy()  # Close the popup window
            else:
                messagebox.showerror("Error", "Insufficient quantity")
        else:
            messagebox.showerror("Error", "Product not found")

    def show_transactions(self):
        self.transaction_window = tk.Toplevel()
        self.transaction_window.title("Transactions")

        transactions = self.db_cursor.execute("SELECT * FROM transactions").fetchall()

        tk.Label(self.transaction_window, text="Name").grid(row=0, column=0)
        tk.Label(self.transaction_window, text="Price").grid(row=0, column=1)
        tk.Label(self.transaction_window, text="Quantity").grid(row=0, column=2)
        tk.Label(self.transaction_window, text="Total Cost").grid(row=0, column=3)
        tk.Label(self.transaction_window, text="Type").grid(row=0, column=4)

        for i, transaction in enumerate(transactions, start=1):
            tk.Label(self.transaction_window, text=transaction[1]).grid(row=i, column=0)
            tk.Label(self.transaction_window, text=transaction[2]).grid(row=i, column=1)
            tk.Label(self.transaction_window, text=transaction[3]).grid(row=i, column=2)
            tk.Label(self.transaction_window, text=transaction[4]).grid(row=i, column=3)
            tk.Label(self.transaction_window, text=transaction[5]).grid(row=i, column=4)

root = tk.Tk()
app = ProductManager(root)
root.mainloop()
