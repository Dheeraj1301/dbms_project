import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image  # Import PIL to open local images

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Geetha$2500",
        database="inventory_db"
    )

# --- Add Product ---
def add_product(name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, quantity, price, supplier) VALUES (%s, %s, %s, %s, %s)",
                   (name, category, quantity, price, supplier))
    conn.commit()
    conn.close()

# --- View Products ---
def get_all_products():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM products", conn)
    conn.close()
    return df

# --- Update Product ---
def update_product(id, name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products SET name=%s, category=%s, quantity=%s, price=%s, supplier=%s WHERE id=%s
    """, (name, category, quantity, price, supplier, id))
    conn.commit()
    conn.close()

# --- Authentication ---
def check_login(username, password):
    return username == "admin" and password == "Dheeraj2500$"

# --- Login UI ---
def login_page():
    st.markdown("<h1 style='text-align:center;color:#4A90E2;'>Welcome to AI Inventory Manager</h1>", unsafe_allow_html=True)
    
    # Load local image (make sure the file is in your working directory)
    try:
        img = Image.open("OIP.jpeg")  # <-- Replace with your downloaded image filename
        st.image(img, use_container_width=True)
    except FileNotFoundError:
        st.error("Local image 'warehouse.jpg' not found. Please place it in the same folder as this script.")

    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")

# --- Dashboard ---
def show_dashboard():
    st.subheader("📊 Inventory Dashboard")
    df = get_all_products()
    
    if df.empty:
        st.warning("No data available.")
        return

    st.write("### Product Summary")
    st.dataframe(df)

    st.write("### Quantity by Category")
    fig, ax = plt.subplots()
    df.groupby("category")["quantity"].sum().plot(kind="bar", ax=ax, color="skyblue")
    st.pyplot(fig)

    st.write("### Stock Value by Supplier")
    df["stock_value"] = df["quantity"] * df["price"]
    fig2, ax2 = plt.subplots()
    df.groupby("supplier")["stock_value"].sum().plot(kind="pie", ax=ax2, autopct='%1.1f%%', figsize=(5,5))
    ax2.set_ylabel("")
    st.pyplot(fig2)

# --- Main App ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.title("Inventory Menu")
        choice = st.sidebar.selectbox("Select an Option", ["Add Product", "View Products", "Update Product", "Dashboard"])

        if choice == "Add Product":
            st.subheader("➕ Add New Product")
            name = st.text_input("Product Name")
            category = st.text_input("Category")
            quantity = st.number_input("Quantity", min_value=0)
            price = st.number_input("Price", min_value=0.0)
            supplier = st.text_input("Supplier")

            if st.button("Add Product"):
                if name and category and supplier:
                    add_product(name, category, quantity, price, supplier)
                    st.success("Product added successfully!")
                else:
                    st.warning("Please fill in all the required fields.")

        elif choice == "View Products":
            st.subheader("📋 All Products")
            df = get_all_products()
            st.dataframe(df)

        elif choice == "Update Product":
            st.subheader("✏️ Update Existing Product")
            df = get_all_products()
            product_ids = df["id"].tolist()
            selected_id = st.selectbox("Select Product ID", product_ids)

            product = df[df["id"] == selected_id].iloc[0]
            name = st.text_input("Product Name", product["name"])
            category = st.text_input("Category", product["category"])
            quantity = st.number_input("Quantity", min_value=0, value=product["quantity"])
            price = st.number_input("Price", min_value=0.0, value=float(product["price"]))
            supplier = st.text_input("Supplier", product["supplier"])

            if st.button("Update Product"):
                update_product(selected_id, name, category, quantity, price, supplier)
                st.success("Product updated successfully!")

        elif choice == "Dashboard":
            show_dashboard()

# --- Run App ---
if __name__ == "__main__":
    main()
