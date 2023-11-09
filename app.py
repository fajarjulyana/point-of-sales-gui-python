import mysql.connector
import tkinter as tk
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

# Koneksi ke database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="posdb"
)
cursor = db.cursor()

# Fungsi untuk menambahkan produk ke database
def add_product():
    name = product_name_entry.get()
    price = float(product_price_entry.get())
    stock = int(product_stock_entry.get())
    
    query = "INSERT INTO products (product_name, price, stock) VALUES (%s, %s, %s)"
    values = (name, price, stock)
    cursor.execute(query, values)
    db.commit()
    messagebox.showinfo("Info", "Produk ditambahkan!")
    clear_product_entries()
    list_products()

# Fungsi untuk melakukan transaksi
def make_transaction():
    product_id = int(product_id_entry.get())
    quantity = int(quantity_entry.get())

    query = "SELECT product_name, price, stock FROM products WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()

    if result:
        product_name, price, stock = result
        if stock >= quantity:
            total_amount = price * quantity
            query = "INSERT INTO transactions (product_id, quantity, total_amount) VALUES (%s, %s, %s)"
            cursor.execute(query, (product_id, quantity, total_amount))
            db.commit()
            messagebox.showinfo("Info", f"Transaksi berhasil! Harga total: ${total_amount:.2f}")
            # Kurangi stok produk
            query = "UPDATE products SET stock = stock - %s WHERE product_id = %s"
            cursor.execute(query, (quantity, product_id))
            db.commit()
        else:
            messagebox.showwarning("Peringatan", "Stok tidak mencukupi.")
    else:
        messagebox.showerror("Kesalahan", "Produk tidak ditemukan.")
    clear_transaction_entries()
    list_products()

# Fungsi untuk menampilkan daftar produk
def list_products():
    query = "SELECT product_id, product_name, price, stock FROM products"
    cursor.execute(query)
    products = cursor.fetchall()
    product_listbox.delete(0, tk.END)  # Hapus item yang ada di listbox
    for product in products:
        product_id, product_name, price, stock = product
        product_listbox.insert(tk.END, f"{product_id}: {product_name} - Harga: ${price:.2f} - Stok: {stock}")

# Fungsi untuk membersihkan entri produk
def clear_product_entries():
    product_name_entry.delete(0, tk.END)
    product_price_entry.delete(0, tk.END)
    product_stock_entry.delete(0, tk.END)

# Fungsi untuk membersihkan entri transaksi
def clear_transaction_entries():
    product_id_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

# Fungsi untuk mencetak transaksi ke dalam dokumen PDF
def print_transaction(transaction_id):
    query = "SELECT t.transaction_id, p.product_name, t.quantity, p.price, t.total_amount " \
            "FROM transactions t " \
            "JOIN products p ON t.product_id = p.product_id " \
            "WHERE t.transaction_id = %s"
    cursor.execute(query, (transaction_id,))
    result = cursor.fetchall()

    if not result:
        messagebox.showerror("Kesalahan", "Transaksi tidak ditemukan.")
        return

    # Nama dokumen PDF
    pdf_filename = f"transaksi_{transaction_id}.pdf"

    # Membuat dokumen PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    # Menambahkan judul
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Struk Transaksi")

    # Tanggal transaksi
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Tanggal: {current_date}")

    # Menambahkan detail transaksi
    c.setFont("Helvetica", 12)
    y = 700
    for row in result:
        transaction_id, product_name, quantity, price, total_amount = row
        c.drawString(100, y, f"{product_name} - Jumlah: {quantity} - Harga: ${price:.2f}")
        y -= 20
    c.drawString(100, y, "-----------------------")
    y -= 20
    c.drawString(100, y, f"Total Harga: ${sum(row[4] for row in result):.2f}")

    # Simpan dokumen PDF
    c.save()

    # Munculkan pesan berhasil
    messagebox.showinfo("Info", f"Transaksi berhasil dicetak ke '{pdf_filename}'")

# Fungsi untuk mencetak transaksi berdasarkan ID transaksi
def print_transaction_by_id():
    transaction_id = int(print_transaction_entry.get())
    print_transaction(transaction_id)

# Membuat jendela utama
root = tk.Tk()
root.title("Aplikasi POS")

# Label dan entry untuk menambah produk
product_name_label = tk.Label(root, text="Nama Produk:")
product_name_label.pack()
product_name_entry = tk.Entry(root)
product_name_entry.pack()

product_price_label = tk.Label(root, text="Harga:")
product_price_label.pack()
product_price_entry = tk.Entry(root)
product_price_entry.pack()

product_stock_label = tk.Label(root, text="Stok:")
product_stock_label.pack()
product_stock_entry = tk.Entry(root)
product_stock_entry.pack()

add_product_button = tk.Button(root, text="Tambah Produk", command=add_product)
add_product_button.pack()

# Label dan entry untuk transaksi
product_id_label = tk.Label(root, text="ID Produk:")
product_id_label.pack()
product_id_entry = tk.Entry(root)
product_id_entry.pack()

quantity_label = tk.Label(root, text="Jumlah:")
quantity_label.pack()
quantity_entry = tk.Entry(root)
quantity_entry.pack()

make_transaction_button = tk.Button(root, text="Transaksi", command=make_transaction)
make_transaction_button.pack()

# Listbox untuk menampilkan produk
product_listbox = tk.Listbox(root)
product_listbox.pack()
list_products()  # Menampilkan daftar produk saat aplikasi pertama kali dijalankan

# Entry untuk mencetak transaksi
print_transaction_label = tk.Label(root, text="ID Transaksi:")
print_transaction_label.pack()
print_transaction_entry = tk.Entry(root)
print_transaction_entry.pack()

print_transaction_button = tk.Button(root, text="Cetak Transaksi", command=print_transaction_by_id)
print_transaction_button.pack()

# Memulai GUI
root.geometry("800x600")  # Ubah ukuran jendela sesuai kebutuhan
root.mainloop()
