import streamlit as st
import mysql.connector
from datetime import datetime

# ----------------------- DB Connection -----------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Geetha",  # Replace with your actual MySQL password
        database="inventory_db"
    )

# ----------------------- DB Functions -----------------------
def add_product(name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, quantity, price, supplier)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, category, quantity, price, supplier))
    conn.commit()
    conn.close()

def view_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()
    return data

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

def update_product(product_id, name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name=%s, category=%s, quantity=%s, price=%s, supplier=%s
        WHERE id=%s
    """, (name, category, quantity, price, supplier, product_id))
    conn.commit()
    conn.close()

# ----------------------- Login -----------------------
def login(username, password):
    return username == "admin" and password == "inventory123"

# ----------------------- App Layout -----------------------
def main_app():
    st.title("🍽️ Inventory Management System")

    menu = ["➕ Add Product", "📦 View Inventory", "✏️ Update Product", "🗑️ Delete Product"]
    choice = st.sidebar.selectbox("Menu", menu)

    food_emojis = {
        "🍕 Pizza": "Pizza",
        "🍔 Burger": "Burger",
        "🍟 Fries": "Fries",
        "🍩 Donut": "Donut",
        "🥤 Soft Drink": "Soft Drink",
        "🥗 Salad": "Salad"
    }

    if choice == "➕ Add Product":
        st.subheader("➕ Add New Product")
        name = st.selectbox("Product Name", list(food_emojis.keys()))
        category = st.text_input("Category (e.g., Fast Food, Beverage)")
        quantity = st.number_input("Quantity", min_value=0)
        price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")
        supplier = st.text_input("Supplier Name")
        
        if st.button("Add Product"):
            add_product(food_emojis[name], category, quantity, price, supplier)
            st.success(f"{name} added to inventory!")

    elif choice == "📦 View Inventory":
        st.subheader("📋 Inventory List")
        data = view_products()
        if data:
            for row in data:
                st.write(f"🆔 **ID:** {row[0]} | 🍽️ **Name:** {row[1]} | 📁 **Category:** {row[2]} | 📦 **Qty:** {row[3]} | 💸 **Price:** ₹{row[4]} | 🚚 **Supplier:** {row[5]}")
            st.success("Inventory displayed!")
        else:
            st.info("No products in inventory.")

    elif choice == "✏️ Update Product":
        st.subheader("✏️ Update Product")
        data = view_products()
        product_ids = [i[0] for i in data]
        if not product_ids:
            st.warning("No products available to update.")
            return
        selected_id = st.selectbox("Select Product ID", product_ids)

        product = [i for i in data if i[0] == selected_id][0]

        name = st.text_input("Product Name", value=product[1])
        category = st.text_input("Category", value=product[2])
        quantity = st.number_input("Quantity", min_value=0, value=product[3])
        price = st.number_input("Price", min_value=0.0, format="%.2f", value=float(product[4]))
        supplier = st.text_input("Supplier", value=product[5])
        
        if st.button("Update"):
            update_product(selected_id, name, category, quantity, price, supplier)
            st.success("Product updated!")

    elif choice == "🗑️ Delete Product":
        st.subheader("🗑️ Delete Product")
        data = view_products()
        product_ids = [i[0] for i in data]
        if not product_ids:
            st.warning("No products available to delete.")
            return
        selected_id = st.selectbox("Select Product ID", product_ids)
        
        if st.button("Delete"):
            delete_product(selected_id)
            st.success("Product deleted successfully!")

# ----------------------- Login Page -----------------------
def login_page():
    st.title("🔐 Login to Inventory System")
    st.write("Please login with your credentials:")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        if login(username, password):
            st.success("Login successful!")
            st.session_state["authenticated"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# ----------------------- Run App -----------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state["authenticated"]:
    main_app()
else:
    login_page()
