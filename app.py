import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import base64

# --- Background Image Function ---
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Custom CSS ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6, label, p {
        font-size: 20px !important;
        font-weight: 600;
    }
    .stTextInput>div>div>input {
        width: 250px !important;
        font-size: 16px !important;
    }
    .stNumberInput>div>div>input {
        width: 120px !important;
        font-size: 16px !important;
    }
    .stButton>button {
        font-size: 18px !important;
        padding: 0.4em 2em;
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
    }
    .login-box {
        background: rgba(255, 255, 255, 0.8);
        padding: 40px;
        border-radius: 10px;
        max-width: 400px;
        margin: auto;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- DB Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Geetha$2500",
        database="inventory_db"
    )

# --- DB Methods ---
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

def delete_product(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    conn.close()

# --- Auth ---
def check_login(username, password):
    return username == "admin" and password == "Dheeraj2500$"

# --- Login Page ---
def login_page():
    set_background("background.jpg")
    st.markdown("<h1 style='text-align:center;color:#1F77B4;'>AI Inventory Manager</h1>", unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    username = st.text_input("Username")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        password = st.text_input("Password", type="password", key="password_input")
    with col2:
        if st.button("Show"):
            st.session_state["show_password"] = not st.session_state.get("show_password", False)

    if st.session_state.get("show_password", False):
        password = st.text_input("Password (visible)", value=password, type="default", key="password_visible")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Dashboard Page ---
def show_dashboard():
    st.subheader("📊 Inventory Dashboard")
    df = get_all_products()

    if df.empty:
        st.warning("No data available.")
        return

    st.write("### Product Summary")
    st.dataframe(df)

    st.write("### Quantity by Category")
    fig1 = px.bar(df.groupby("category")["quantity"].sum().reset_index(),
                  x="category", y="quantity", color="category",
                  title="Total Quantity per Category")
    st.plotly_chart(fig1, use_container_width=True)

    st.write("### Stock Value by Supplier")
    df["stock_value"] = df["quantity"] * df["price"]
    fig2 = px.pie(df, names="supplier", values="stock_value", title="Stock Value Distribution by Supplier")
    st.plotly_chart(fig2, use_container_width=True)

# --- Main App ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.title("📦 Inventory Menu")
        choice = st.sidebar.radio("Choose Action", ["➕ Add Product", "📋 View Products", "✏️ Update Product", "🗑️ Delete Product", "📊 Dashboard", "🚪 Logout"])

        if choice != "📊 Dashboard":
            set_background("background.jpg")  # Background for all except Dashboard

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
            st.dataframe(df)

        elif choice == "✏️ Update Product":
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
                st.success("✅ Product updated successfully!")

        elif choice == "🗑️ Delete Product":
            st.subheader("🗑️ Delete Product (Password Protected)")
            delete_pass = st.text_input("Enter Delete Password", type="password")
            if delete_pass == "DeleteSecure123$":
                df = get_all_products()
                product_ids = df["id"].tolist()
                selected_id = st.selectbox("Select Product ID to Delete", product_ids)
                if st.button("Confirm Delete"):
                    delete_product(selected_id)
                    st.success("🗑️ Product deleted successfully!")
            elif delete_pass != "":
                st.error("❌ Incorrect password!")

        elif choice == "📊 Dashboard":
            show_dashboard()

        elif choice == "🚪 Logout":
            st.session_state.logged_in = False
            st.experimental_rerun()

# --- Run App ---
if __name__ == "__main__":
    main()
