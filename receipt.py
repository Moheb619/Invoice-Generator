import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry  # Import DateEntry for the calendar widget
from fpdf import FPDF
from datetime import datetime
import random
import os


# PDF Generator Class (modified to accept date)
class ReceiptPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.is_last_page = False  # Track if the current page is the last

        # Set increased margins: left, top, right
        self.set_margins(20, 20, 20)  # 20 mm margins on all sides
        # Adjusted the bottom margin to accommodate all footer elements
        self.set_auto_page_break(auto=True, margin=60)  # Auto page break with 60 mm bottom margin

    def header(self):
        # Define dimensions
        logo_width = 30  # Width of the logo in mm
        logo_height = 30  # Height of the logo in mm
        space_between = 10  # Space between logo and text in mm

        # Define header position
        header_y = 20  # Top margin in mm (aligned with increased margin)

        # Set font for the header - Increase size for larger and bold text
        font_size = 24  # Increased font size
        font_style = "B"  # Bold
        self.set_font("Arial", font_style, font_size)
        text = "MAA MEDICAL CENTER"
        text_width = self.get_string_width(text)

        # Calculate total width of logo and text
        total_width = logo_width + space_between + text_width

        # Calculate the starting x position to center the logo and text
        start_x = (self.w - total_width) / 2

        # Insert the logo with error handling
        logo_path = "build/logo.png"
        if os.path.exists(logo_path):
            self.image(logo_path, x=start_x, y=header_y, w=logo_width, h=logo_height)
        else:
            # Handle missing image, e.g., log a warning or use a placeholder
            print(f"Warning: Logo image not found at {logo_path}. Skipping logo.")

        # Calculate the vertical position to center the text relative to the logo
        text_height = font_size * 0.3528  # Convert font size from points to mm
        text_y = header_y + (logo_height - text_height) / 2

        # Position the text right next to the logo
        self.set_xy(start_x + logo_width + space_between, text_y)
        self.cell(text_width, text_height, text, border=0, ln=0, align='L')

        # Calculate the position for the custom underline
        underline_thickness = 0.5  # Thickness of the underline in mm
        underline_spacing = 2  # Space between text and underline in mm
        underline_y = text_y + text_height + underline_spacing

        # Draw the custom underline
        self.set_line_width(underline_thickness)
        self.line(
            start_x + logo_width + space_between,
            underline_y,
            start_x + logo_width + space_between + text_width,
            underline_y
        )

        # Move to the next line after the header
        max_header_y = header_y + logo_height
        self.set_y(max_header_y + 10)  # Add 10 mm space below the header

        # Set font for the subtitle or additional information
        self.set_font("Arial", size=10)

        # Add the multi-line cell with centered alignment within the margins
        self.set_x(self.l_margin)
        self.multi_cell(
            0,
            5,
            "Drugs, Operation Disposables, CT, MRI, ANGIOGRAM, PET CT Contrast, Medicine Supplier\n166/5 Matikata MP Check Post, Dhaka Cantonment, Dhaka-1206",
            align="C"
        )

        # Add some space after the header section
        self.ln(10)

    def footer(self):
        # Set the font for the footer
        self.set_font("Arial", "I", 8)

        if self.is_last_page:
            # Signature Section
            self.set_y(-60)  # Position 60 mm from the bottom
            self.set_font("Arial", size=10)
            self.set_x(self.l_margin)
            
            # Customer Signature
            self.cell(70, 10, "__________________________", align="L", ln=0)
            # Spacer
            self.cell(31, 10, "", ln=0)
            # Maa Medical Center Signature
            self.cell(70, 10, "__________________________", align="R", ln=1)
            
            # Labels for Signatures
            self.set_x(self.l_margin)
            self.cell(70, 5, "Customer Signature", align="L", ln=0)
            self.cell(31, 5, "", ln=0)
            self.cell(70, 5, "Maa Medical Center Thank You", align="R", ln=1)
            
            # Add spacing between signatures and "Sold Items Not Taken"
            self.ln(10)  # Add 10 mm space

        # "Sold Items Not Taken" Section
        self.set_y(-35)  # Position 35 mm from the bottom
        self.set_font("Arial", "B", 10)
        self.set_x(self.l_margin)
        self.cell(0, 10, "Sold Items Not Taken", border=1, align="C", ln=1)

        # "MAA MEDICAL CENTER" at the very bottom
        self.set_y(-15)  # Position 15 mm from the bottom
        self.set_font("Arial", "I", 8)
        self.set_x(self.l_margin)
        self.cell(0, 10, "MAA MEDICAL CENTER " * 5, align="C")


    def customer_details(self, name, address, mobile):
        self.set_font("Arial", size=10)
        self.set_x(self.l_margin)
        self.cell(0, 10, f"Name: {name}", ln=True)
        self.set_x(self.l_margin)
        self.cell(0, 10, f"Address: {address}", ln=True)
        self.set_x(self.l_margin)
        self.cell(0, 10, f"Mobile No: {mobile}", ln=True)
        self.ln(10)

    def invoice_details(self, invoice_no, date):
        self.set_font("Arial", size=10)
        self.set_x(self.l_margin)
        self.cell(100, 10, f"INVOICE NUMBER: {invoice_no}", ln=0, align="L")
        self.cell(0, 10, f"Date: {date}", ln=1, align="R")
        self.ln(5)

    def add_table(self, medicines, advance):
        # Define column names and their width percentages
        columns = [
            {"title": "SL No", "percentage": 0.15},
            {"title": "Medicine Details", "percentage": 0.45},
            {"title": "QTY", "percentage": 0.10},
            {"title": "Price", "percentage": 0.15},
            {"title": "Amount", "percentage": 0.15},
        ]

        # Calculate the effective page width (A4 width - left margin - right margin)
        effective_width = self.w - 2 * self.l_margin

        # Calculate column widths based on percentages
        col_widths = {col["title"]: col["percentage"] * effective_width for col in columns}

        # Set the x position for the table to align with left margin
        self.set_x(self.l_margin)

        # Set font for table header
        self.set_font("Arial", "B", 10)

        # Create table header
        for col in columns:
            self.cell(col_widths[col["title"]], 10, col["title"], 1, align="C")
        self.ln()

        # Set font for table body
        self.set_font("Arial", size=10)
        total_amount = 0

        for idx, medicine in enumerate(medicines, 1):
            description, qty, price = medicine
            amount = qty * price
            total_amount += amount

            # Determine the maximum number of lines for the Medicine Details
            # Calculate number of lines needed
            description_lines = self.get_multi_cell_lines(col_widths["Medicine Details"], 10, description)

            # Define row height based on number of lines (10 mm per line)
            row_height = 10 * description_lines

            # Check if a new page is needed
            # Adjusted reserved space from 60 to 60 mm to align with the new footer margin
            if self.get_y() + row_height > self.h - 60:
                self.add_page()
                # Recreate table header on the new page
                self.set_x(self.l_margin)
                self.set_font("Arial", "B", 10)
                for col in columns:
                    self.cell(col_widths[col["title"]], 10, col["title"], 1, align="C")
                self.ln()
                self.set_font("Arial", size=10)

            # Save the current x and y positions
            x_before = self.get_x()
            y_before = self.get_y()

            # Draw the SL No cell
            self.set_x(self.l_margin)
            self.cell(col_widths["SL No"], row_height, str(idx), 1, align="C", ln=0, fill=False)

            # Draw the Medicine Details cell with multi_cell
            self.multi_cell(col_widths["Medicine Details"], 10, description, border=1, align="L")
            # After multi_cell, the cursor moves to the next line. We need to reset x and y
            # to continue drawing the rest of the cells in the row
            self.set_xy(x_before + col_widths["SL No"] + col_widths["Medicine Details"], y_before)

            # Draw the QTY cell
            self.cell(col_widths["QTY"], row_height, str(qty), 1, align="C", ln=0, fill=False)

            # Draw the Price cell
            self.cell(col_widths["Price"], row_height, f"{price:.2f}", 1, align="C", ln=0, fill=False)

            # Draw the Amount cell
            self.cell(col_widths["Amount"], row_height, f"{amount:.2f}", 1, align="C", ln=1, fill=False)

        # Add Total, Paid, Due rows
        # Calculate label width (sum of SL No, Medicine Details, QTY, Price)
        total_label_width = col_widths["SL No"] + col_widths["Medicine Details"] + col_widths["QTY"] + col_widths["Price"]

        # Total
        self.set_font("Arial", "B", 10)
        self.set_x(self.l_margin)
        self.cell(total_label_width, 10, "Total ", 1, align="R")
        self.cell(col_widths["Amount"], 10, f"{total_amount:.2f}", 1, align="C")
        self.ln()

        # Paid
        self.set_x(self.l_margin)
        self.cell(total_label_width, 10, "Paid ", 1, align="R")
        self.cell(col_widths["Amount"], 10, f"{advance:.2f}", 1, align="C")
        self.ln()

        # Due
        due = total_amount - advance
        self.set_x(self.l_margin)
        self.cell(total_label_width, 10, "Due ", 1, align="R")
        self.cell(col_widths["Amount"], 10, f"{due:.2f}", 1, align="C")
        self.ln()

        # Add the amount in words
        self.set_font("Arial", size=10)
        self.set_x(self.l_margin)
        self.multi_cell(0, 10, f"Taka (in Words): {self.number_to_words(int(total_amount))} Taka Only.", align="L")

        # Add extra spacing before the footer
        self.ln(10)  # Reduced from 15 to 10 to prevent pushing content into the footer

    def get_multi_cell_lines(self, width, height, text):
        """
        Helper method to calculate the number of lines needed for a given text in a multi_cell.
        """
        # Temporarily set the cell to calculate the number of lines
        original_font = self.font_family, self.font_style, self.font_size_pt
        self.set_font(*original_font)
        # Split the text into lines that fit within the cell width
        lines = self.multi_cell(width, height, text, border=0, align='L', split_only=True)
        return len(lines) if lines else 1

    def finalize_last_page(self):
        self.is_last_page = True

    def number_to_words(self, n):
        """
        Converts a number into words.
        """
        units = ["", "One", "Two", "Three", "Four", "Five", "Six",
                 "Seven", "Eight", "Nine"]
        teens = ["", "Eleven", "Twelve", "Thirteen", "Fourteen",
                 "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty",
                "Sixty", "Seventy", "Eighty", "Ninety"]
        thousands = ["", "Thousand", "Million", "Billion"]

        def convert_chunk(chunk):
            words = []
            if chunk >= 100:
                words.append(units[chunk // 100] + " Hundred")
                chunk %= 100
            if 10 < chunk < 20:
                words.append(teens[chunk - 10])
            else:
                if chunk >= 10:
                    words.append(tens[chunk // 10])
                if chunk % 10 > 0:
                    words.append(units[chunk % 10])
            return " ".join(words)

        if n == 0:
            return "Zero"

        words = []
        chunk_count = 0
        while n > 0:
            chunk = n % 1000
            if chunk > 0:
                words.append(convert_chunk(chunk) + " " + thousands[chunk_count])
            n //= 1000
            chunk_count += 1

        return " ".join(reversed(words)).strip()


# Validation Functions
def validate_digit_only(P):
    """Allow only digits.Return True or False"""
    return P.isdigit() or P == ""


def validate_decimal(P):
    """Allow only digits and at most one decimal point."""
    if P == "":
        return True
    if P.count('.') > 1:
        return False
    for char in P:
        if not (char.isdigit() or char == '.'):
            return False
    return True


# PDF Generator Function (modified to accept date)
def generate_receipt(medicines, date_str):
    customer_name = entry_name.get().strip()
    customer_address = entry_address.get().strip()
    customer_mobile = entry_mobile.get().strip()
    advance_amount = entry_advance.get().strip()

    if not customer_name:
        messagebox.showerror("Input Error", "Name is required.")
        return

    if not customer_mobile.isdigit():
        messagebox.showerror("Input Error", "Mobile number must contain only digits.")
        return

    if not advance_amount:
        messagebox.showerror("Input Error", "Paid amount is required.")
        return

    try:
        advance = float(advance_amount)
    except ValueError:
        messagebox.showerror("Input Error", "Advance amount must contain only digits and at most one decimal point.")
        return

    if not medicines:
        messagebox.showerror("Input Error", "At least one medicine must be added to generate the receipt.")
        return

    # Calculate total amount
    total_amount = sum(qty * price for _, qty, price in medicines)
    if advance > total_amount:
        messagebox.showerror("Input Error", f"Paid amount ({advance:.2f}) cannot exceed the total amount ({total_amount:.2f}).")
        return

    # Parse the selected date from 'dd/mm/yyyy' to 'yyyy-mm-dd'
    try:
        selected_date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Date Error", "Invalid date format. Please select a valid date.")
        return

    # Create invoice ID and filename
    invoice_number = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    sanitized_name = customer_name.replace(" ", "_").replace("/", "-")
    pdf_filename = f"receipt_{invoice_number}_{sanitized_name}.pdf"

    # Create a folder for the selected date
    date_folder = f"Receipts/{selected_date}"  # e.g., "Receipts/2024-09-15"
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)  # Create the folder if it doesn't exist

    # Full path to save the PDF
    pdf_path = os.path.join(date_folder, pdf_filename)

    # Generate the PDF
    pdf = ReceiptPDF()
    pdf.add_page()
    pdf.invoice_details(invoice_no=invoice_number, date=date_str)  # Pass the selected date in original format
    pdf.customer_details(name=customer_name, address=customer_address, mobile=customer_mobile)
    pdf.add_table(medicines, advance)
    pdf.finalize_last_page()
    pdf.output(pdf_path)

    # Show success message
    messagebox.showinfo("Success", f"Receipt saved as {pdf_path}")

    # Auto-open the PDF file
    try:
        os.startfile(pdf_path)  # For Windows
    except AttributeError:
        try:
            os.system(f"open {pdf_path}")  # For macOS
        except Exception:
            os.system(f"xdg-open {pdf_path}")  # For Linux

    # Clear the form
    clear_form()


# Function to clear the form
def clear_form():
    """
    Clears all input fields and the medicine table.
    """
    # Clear customer details
    entry_name.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    entry_mobile.delete(0, tk.END)
    entry_advance.delete(0, tk.END)
    date_entry.set_date(datetime.now())  # Reset date to today

    # Clear medicine fields
    entry_description.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)

    # Clear the table and medicines list
    global medicines
    medicines = []
    update_medicine_list(medicines)


# Function to add a medicine
def add_medicine(medicines):
    description = entry_description.get().strip()
    try:
        qty = int(entry_qty.get().strip())
        price = float(entry_price.get().strip())
    except ValueError:
        messagebox.showerror("Input Error", "Quantity must be an integer and Price must be a number.")
        return

    if not description or not entry_price.get() or not entry_qty.get():
        messagebox.showerror("Input Error", "Medicine Details, Quantity, and Price are required fields.")
        return

    if price <= 0:
        messagebox.showerror("Input Error", "Price must be greater than 0.")
        return

    for med in medicines:
        if med[0] == description:
            messagebox.showerror("Input Error", "This medicine description already exists.")
            return

    medicines.append((description, qty, price))
    update_medicine_list(medicines)
    entry_description.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)


# Function to select a medicine from the treeview
def select_medicine(event):
    """
    Populates the input fields with the details of the selected medicine for editing.
    """
    selected_item = tree.focus()
    if not selected_item:
        return
    values = tree.item(selected_item, 'values')
    if values:
        entry_description.delete(0, tk.END)
        entry_description.insert(0, values[1])  # Medicine Details
        entry_qty.delete(0, tk.END)
        entry_qty.insert(0, values[2])  # Quantity
        entry_price.delete(0, tk.END)
        entry_price.insert(0, values[3])  # Price


# Function to update a selected medicine
def update_medicine(medicines):
    """
    Updates the selected medicine with the details entered in the input fields.
    """
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Selection Error", "No medicine selected for updating.")
        return

    description = entry_description.get().strip()
    try:
        qty = int(entry_qty.get().strip())
        price = float(entry_price.get().strip())
    except ValueError:
        messagebox.showerror("Input Error", "Quantity must be an integer and Price must be a number.")
        return

    if not description or qty <= 0 or price <= 0:
        messagebox.showerror("Input Error", "All fields must be filled with valid values.")
        return

    # Update the medicines list
    for i, (desc, _, _) in enumerate(medicines):
        if desc == tree.item(selected_item, 'values')[1]:
            medicines[i] = (description, qty, price)
            break

    # Update the table and clear input fields
    update_medicine_list(medicines)
    entry_description.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)


# Function to delete a selected medicine
def delete_medicine(medicines):
    """
    Deletes the selected medicine from the table and the medicines list.
    """
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Selection Error", "No medicine selected for deletion.")
        return

    # Find and remove the medicine from the list
    selected_desc = tree.item(selected_item, 'values')[1]
    medicines[:] = [med for med in medicines if med[0] != selected_desc]

    # Update the table
    update_medicine_list(medicines)


# Function to update the total amount label
def update_total_amount():
    total = sum(qty * price for _, qty, price in medicines)
    total_label.config(text=f"Total Amount: {total:.2f}")


# Function to update the medicine list in the treeview
def update_medicine_list(medicines):
    for row in tree.get_children():
        tree.delete(row)
    for idx, (description, qty, price) in enumerate(medicines, start=1):
        tree.insert("", "end", values=(idx, description, qty, price, qty * price))
    update_total_amount()


# Function to generate dummy data
def generate_dummy_data():
    global medicines
    medicines = [
        (f"Medicine {i}", random.randint(1, 10), round(random.uniform(50.0, 500.0), 2))
        for i in range(1, 21)
    ]
    update_medicine_list(medicines)


# Tkinter app setup
app = tk.Tk()
app.title("Money Receipt (Maa Medical Center)")
app.geometry("")  # Set a fixed window size for better layout control

# Register validation commands
validate_digit = app.register(validate_digit_only)
validate_decimal_cmd = app.register(validate_decimal)

medicines = []

# Customer Details Frame
tk.Label(app, text="Customer Details", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(app, text="Name:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
entry_name = tk.Entry(app, width=40)
entry_name.grid(row=1, column=1, sticky="w", padx=10, pady=5)

tk.Label(app, text="Address:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
entry_address = tk.Entry(app, width=40)
entry_address.grid(row=2, column=1, sticky="w", padx=10, pady=5)

tk.Label(app, text="Mobile No:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
entry_mobile = tk.Entry(app, width=40, validate="key", validatecommand=(validate_digit, "%P"))
entry_mobile.grid(row=3, column=1, sticky="w", padx=10, pady=5)

# Date Field
tk.Label(app, text="Date:").grid(row=4, column=0, sticky="e", padx=10, pady=5)
date_entry = DateEntry(app, width=37, background='darkblue',
                       foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
date_entry.set_date(datetime.now())  # Set default date to today
date_entry.grid(row=4, column=1, sticky="w", padx=10, pady=5)

# Medicine Details Frame
tk.Label(app, text="Medicine Details", font=("Arial", 14)).grid(row=5, column=0, columnspan=2, pady=10)

tk.Label(app, text="Medicine Details:").grid(row=6, column=0, sticky="e", padx=10, pady=5)
entry_description = tk.Entry(app, width=30)
entry_description.grid(row=6, column=1, sticky="w", padx=10, pady=5)

tk.Label(app, text="Quantity:").grid(row=7, column=0, sticky="e", padx=10, pady=5)
entry_qty = tk.Entry(app, width=10, validate="key", validatecommand=(validate_digit, "%P"))
entry_qty.grid(row=7, column=1, sticky="w", padx=10, pady=5)

tk.Label(app, text="Price:").grid(row=8, column=0, sticky="e", padx=10, pady=5)
entry_price = tk.Entry(app, width=10, validate="key", validatecommand=(validate_decimal_cmd, "%P"))
entry_price.grid(row=8, column=1, sticky="w", padx=10, pady=5)

# Add Medicine Button
tk.Button(app, text="Add Medicine", command=lambda: add_medicine(medicines)).grid(
    row=9, column=1, pady=10, sticky="w")

# Medicines Treeview
tree = ttk.Treeview(app, columns=("SL No", "Medicine Details", "Quantity", "Price", "Amount"), show="headings")
tree.grid(row=10, column=0, columnspan=2, padx=20, pady=10)
tree.heading("SL No", text="SL No")
tree.heading("Medicine Details", text="Medicine Details")
tree.heading("Quantity", text="Quantity")
tree.heading("Price", text="Price")
tree.heading("Amount", text="Amount")

tree.bind("<<TreeviewSelect>>", select_medicine)

# Update and Delete Buttons
tk.Button(app, text="Update Medicine", command=lambda: update_medicine(medicines)).grid(
    row=11, column=0, pady=10, sticky="w", padx=10)
tk.Button(app, text="Delete Medicine", command=lambda: delete_medicine(medicines)).grid(
    row=11, column=1, pady=10, sticky="e", padx=10)

# Paid Amount Field (Moved below Update/Delete buttons)
tk.Label(app, text="Paid Amount:").grid(row=12, column=0, sticky="e", padx=10, pady=5)
entry_advance = tk.Entry(app, width=20, validate="key", validatecommand=(validate_decimal_cmd, "%P"))
entry_advance.grid(row=12, column=1, sticky="w", padx=10, pady=5)

# Total Amount Label
total_label = tk.Label(app, text="Total Amount: 0.00", font=("Arial", 12))
total_label.grid(row=13, column=0, columnspan=2, pady=10)

# Generate Receipt Button
tk.Button(app, text="Generate Receipt",
          command=lambda: generate_receipt(medicines, date_entry.get())).grid(
    row=14, column=0, columnspan=2, pady=20)

# Generate Dummy Data Button
tk.Button(app, text="Generate Dummy Data", command=generate_dummy_data).grid(
    row=15, column=0, columnspan=2, pady=10)


# Start the Tkinter event loop
app.mainloop()
