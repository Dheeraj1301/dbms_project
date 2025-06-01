import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from PIL import Image
import base64

# ---------- Configuration ----------
BACKGROUND_IMAGE_PATH = "inven.jpg"  # Place this image in your project folder

# ---------- Set Page Configuration ----------
st.set_page_config(layout="wide", page_title="AI Inventory Manager", page_icon="📦")

# ---------- Utility: Set Background ----------
def set_background(image_path, apply_to_dashboard=False):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .login-container {{
        background: rgba(255, 255, 255, 0.7);
        padding: 2rem;
        border-radius: 10px;
        max-width: 500px;
        margin: auto;
    }}
    </style>
    """
    if apply_to_dashboard:
        st.markdown(style, unsafe_allow_html=True)

# ---------- Database Connection ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Geetha$2500",
        database="inventory_db"
    )

# ---------- DB Methods ----------
def add_product(name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, quantity, price, supplier) VALUES (%s, %s, %s, %s, %s)",
                   (name, category, quantity, price, supplier))
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM products", conn)
    conn.close()
    return df

def update_product(id, name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products SET name=%s, category=%s, quantity=%s, price=%s, supplier=%s WHERE id=%s
    """, (name, category, quantity, price, supplier, id))
    conn.commit()
    conn.close()

def delete_product(id, password):
    if password == "Dheeraj2500$":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return True
    return False

# ---------- Authentication ----------
def check_login(username, password):
    return username == "admin" and password == "Dheeraj2500$"

# ---------- Login Page ----------
def login_page():
    set_background(BACKGROUND_IMAGE_PATH, apply_to_dashboard=True)
    st.markdown("<h1 style='text-align:center; color:#fff;'>🔐 AI Inventory Manager</h1>", unsafe_allow_html=True)
    with st.container():
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            st.markdown("</div>", unsafe_allow_html=True)

        if login_btn:
            if check_login(username, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------- Dashboard Page ----------
def show_dashboard():
    st.subheader("📊 Inventory Dashboard")
    df = get_all_products()

    if df.empty:
        st.warning("No data available.")
        return

    st.write("### 📋 Product Summary")
    st.dataframe(df, use_container_width=True)

    st.write("### 📦 Quantity by Category")
    fig1 = px.bar(df.groupby("category")["quantity"].sum().reset_index(),
                  x="category", y="quantity", color="category",
                  title="Total Quantity per Category")
    st.plotly_chart(fig1, use_container_width=True)

    st.write("### 💰 Stock Value by Supplier")
    df["stock_value"] = df["quantity"] * df["price"]
    fig2 = px.pie(df, names="supplier", values="stock_value", title="Stock Value Distribution by Supplier")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Main App ----------
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2921/2921826.png", width=80)
        st.sidebar.title("Inventory Menu")
        choice = st.sidebar.radio("Choose Action", ["➕ Add Product", "📋 View Products", "✏️ Update Product", "❌ Delete Product", "📊 Dashboard", "🔓 Logout"])

        # Apply background only for non-dashboard pages
        if choice not in ["📊 Dashboard"]:
            set_background(BACKGROUND_IMAGE_PATH, apply_to_dashboard=True)

        if choice == "➕ Add Product":
            st.subheader("➕ Add New Product")
            name = st.text_input("Product Name")
            category = st.text_input("Category")
            quantity = st.number_input("Quantity", min_value=0)
            price = st.number_input("Price", min_value=0.0)
            supplier = st.text_input("Supplier")

            if st.button("Add Product"):
                if name and category and supplier:
                    add_product(name, category, quantity, price, supplier)
                    st.success("✅ Product added successfully!")
                else:
                    st.warning("Please fill in all the required fields.")

        elif choice == "📋 View Products":
            st.subheader("📋 All Products")
            df = get_all_products()
            st.dataframe(df, use_container_width=True)

        elif choice == "✏️ Update Product":
            st.subheader("✏️ Update Existing Product")
            df = get_all_products()
            if df.empty:
                st.warning("No products to update.")
                return
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
                st.success("✅ Product updated successfully!")

        elif choice == "❌ Delete Product":
            st.subheader("❌ Delete Product")
            df = get_all_products()
            if df.empty:
                st.warning("No products to delete.")
                return
            product_ids = df["id"].tolist()
            selected_id = st.selectbox("Select Product ID to Delete", product_ids)
            delete_pass = st.text_input("Enter Admin Password", type="password")
            if st.button("Confirm Delete"):
                if delete_product(selected_id, delete_pass):
                    st.success("✅ Product deleted successfully.")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password.")

        elif choice == "📊 Dashboard":
            show_dashboard()

        elif choice == "🔓 Logout":
            st.session_state.logged_in = False
            st.rerun()

# ---------- Run App ----------
if __name__ == "__main__":
    main()
