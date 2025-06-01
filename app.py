import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import os

# --- Constants ---
BACKGROUND_IMAGE_PATH = r"C:/Users/disha/OneDrive/Desktop/inventory_managmement/dbms_project/inven.jpg"  # Adjust path accordingly

# --- CSS Styling ---
def local_css():
    st.markdown(
        f"""
        <style>
        /* Background Image for Login & Inventory pages only */
        .bg-image {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{BACKGROUND_IMAGE_PATH}');
            background-size: cover;
            background-position: center;
            filter: brightness(0.7);
            z-index: -1;
        }}

        /* Translucent Card */
        .translucent-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 25px 30px;
            border-radius: 14px;
            max-width: 400px;
            margin: 3rem auto;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        /* Input Styling */
        input[type="password"], input[type="text"], input[type="number"] {{
            font-size: 16px !important;
            height: 35px !important;
            width: 270px !important;
            padding-right: 40px !important; /* room for eye button */
            border-radius: 5px !important;
            border: 1.5px solid #ccc !important;
            padding-left: 10px !important;
        }}

        /* Hide default password toggle */
        input[type="password"]::-ms-reveal,
        input[type="password"]::-ms-clear,
        input[type="password"]::-webkit-inner-spin-button,
        input[type="password"]::-webkit-outer-spin-button,
        input[type="password"]::-webkit-search-cancel-button,
        input[type="password"]::-webkit-search-decoration {{
            display: none !important;
        }}

        /* Eye toggle button */
        .toggle-btn {{
            position: relative;
            left: -38px;
            top: -38px;
            border: none;
            background: transparent;
            color: white;
            cursor: pointer;
            font-size: 18px;
            outline: none;
            user-select: none;
        }}

        /* Streamlit sidebar styling for better appearance */
        .css-1d391kg {{
            background-color: #ffffff !important;
            border-radius: 8px !important;
            padding: 20px !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            color: #000 !important;
        }}

        /* Buttons bigger font */
        button[kind="primary"] {{
            font-size: 18px !important;
            padding: 8px 25px !important;
            border-radius: 8px !important;
        }}

        /* Headings */
        h1, h2, h3, h4 {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- Set Background Image for Login and Inventory Pages ---
def set_bg_image():
    st.markdown(f'<div class="bg-image"></div>', unsafe_allow_html=True)

# --- Database Connection ---
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
    cursor.execute(
        "INSERT INTO products (name, category, quantity, price, supplier) VALUES (%s, %s, %s, %s, %s)",
        (name, category, quantity, price, supplier),
    )
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
    cursor.execute(
        "UPDATE products SET name=%s, category=%s, quantity=%s, price=%s, supplier=%s WHERE id=%s",
        (name, category, quantity, price, supplier, id),
    )
    conn.commit()
    conn.close()

def delete_product(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    conn.close()

# --- Authentication ---
def check_login(username, password):
    return username == "admin" and password == "Dheeraj2500$"

# --- Login UI ---
def login_page():
    set_bg_image()
    local_css()

    st.markdown("<h1 style='text-align:center; color:#ffffff; font-size:48px;'>🔐 AI Inventory Manager</h1>", unsafe_allow_html=True)

    st.markdown('<div class="translucent-card">', unsafe_allow_html=True)

    username = st.text_input("Username", key="username_input", label_visibility="visible")

    # Password with toggle
    if "show_password" not in st.session_state:
        st.session_state.show_password = False

    pw_col1, pw_col2 = st.columns([5, 1])
    with pw_col1:
        password = st.text_input(
            "Password",
            type="text" if st.session_state.show_password else "password",
            key="password_input",
            label_visibility="visible",
            placeholder="Enter your password",
        )
    with pw_col2:
        toggle_label = "🙈" if st.session_state.show_password else "👁️"
        if st.button(toggle_label, key="toggle_pw", help="Show/Hide password"):
            st.session_state.show_password = not st.session_state.show_password

    if st.button("Login", key="login_btn"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Dashboard ---
def show_dashboard():
    # No background image here, clean UI
    st.markdown(
        """
        <style>
        .css-1d391kg {
            background-color: #ffffff !important;
            border-radius: 8px !important;
            padding: 20px !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            color: #000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("📊 Inventory Dashboard")
    df = get_all_products()

    if df.empty:
        st.warning("No data available.")
        return

    st.write("### Product Summary")
    st.dataframe(df, height=300)

    st.write("### Quantity by Category")
    fig1 = px.bar(
        df.groupby("category")["quantity"].sum().reset_index(),
        x="category",
        y="quantity",
        color="category",
        title="Total Quantity per Category",
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.write("### Stock Value by Supplier")
    df["stock_value"] = df["quantity"] * df["price"]
    fig2 = px.pie(df, names="supplier", values="stock_value", title="Stock Value Distribution by Supplier")
    st.plotly_chart(fig2, use_container_width=True)

# --- Inventory Management Page ---
def inventory_page():
    set_bg_image()
    local_css()

    st.markdown("<h2 style='text-align:center; color:#ffffff;'>📦 Inventory Management</h2>", unsafe_allow_html=True)

    st.markdown('<div class="translucent-card">', unsafe_allow_html=True)

    choice = st.radio("Choose Action", ["➕ Add Product", "📋 View Products", "✏️ Update Product", "🗑️ Delete Product"])

    if choice == "➕ Add Product":
        st.subheader("➕ Add New Product")

        name = st.text_input("Product Name", max_chars=50)
        category = st.text_input("Category", max_chars=30)
        quantity = st.number_input("Quantity", min_value=0, step=1)
        price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f")
        supplier = st.text_input("Supplier", max_chars=50)

        if st.button("Add Product"):
            if not all([name, category, supplier]):
                st.error("Please fill all text fields.")
            else:
                add_product(name, category, quantity, price, supplier)
                st.success(f"✅ Added product '{name}' successfully!")

    elif choice == "📋 View Products":
        st.subheader("📋 Product List")
        df = get_all_products()
        if df.empty:
            st.warning("No products found.")
        else:
            st.dataframe(df)

    elif choice == "✏️ Update Product":
        st.subheader("✏️ Update Existing Product")
        df = get_all_products()
        if df.empty:
            st.warning("No products found.")
        else:
            product_ids = df["id"].tolist()
            selected_id = st.selectbox("Select product to update", product_ids)
            product = df[df["id"] == selected_id].iloc[0]

            name = st.text_input("Product Name", value=product["name"])
            category = st.text_input("Category", value=product["category"])
            quantity = st.number_input("Quantity", min_value=0, step=1, value=int(product["quantity"]))
            price = st.number_input("Price", min_value=0.0, step=0.01, value=float(product["price"]))
            supplier = st.text_input("Supplier", value=product["supplier"])

            if st.button("Update Product"):
                update_product(selected_id, name, category, quantity, price, supplier)
                st.success(f"✅ Updated product '{name}' successfully!")

    elif choice == "🗑️ Delete Product":
        st.subheader("🗑️ Delete Product (Admin only)")

        # Password to confirm delete
        if "del_password" not in st.session_state:
            st.session_state.del_password = ""
        del_password = st.text_input("Enter Admin Password", type="password", key="del_password")

        df = get_all_products()
        if df.empty:
            st.warning("No products found.")
        else:
            product_ids = df["id"].tolist()
            selected_id = st.selectbox("Select product to delete", product_ids)

            if st.button("Delete Product"):
                if del_password == "Dheeraj2500$":
                    delete_product(selected_id)
                    st.success(f"✅ Deleted product with ID {selected_id}!")
                    # Reset password after delete
                    st.session_state.del_password = ""
                else:
                    st.error("❌ Incorrect password. Cannot delete product.")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Main App ---
def main():
    # Initialize session states
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    local_css()

    # Sidebar menu
    st.sidebar.title("Menu")
    if st.session_state.logged_in:
        page = st.sidebar.radio("Go to", ["Dashboard", "Inventory Management", "Logout"])
    else:
        page = st.sidebar.radio("Go to", ["Login"])

    if page == "Login":
        login_page()

    elif page == "Dashboard":
        if not st.session_state.logged_in:
            st.warning("Please login first.")
            login_page()
        else:
            show_dashboard()

    elif page == "Inventory Management":
        if not st.session_state.logged_in:
            st.warning("Please login first.")
            login_page()
        else:
            inventory_page()

    elif page == "Logout":
        st.session_state.logged_in = False
        st.experimental_rerun()


if __name__ == "__main__":
    main()
