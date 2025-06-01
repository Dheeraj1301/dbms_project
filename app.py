import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64

# --- Configuration ---
BACKGROUND_IMAGE_PATH = "C:\\Users\\disha\\OneDrive\\Desktop\\inventory_managmement\\dbms_project\\inven.jpg"  # Replace with your image path
DELETE_PASSWORD = "delete"  # Set your desired delete password

# --- Helper Functions ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(image_path):
    bin_str = get_base64_of_bin_file(image_path)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Geetha$2500",
        database="inventory_db"
    )

# --- Database Operations ---
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

# --- Authentication ---
def check_login(username, password):
    return username == "admin" and password == "Dheeraj2500$"

# --- Export Helpers ---
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventory')
    processed_data = output.getvalue()
    return processed_data

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Login Page ---
def login_page():
    set_background(BACKGROUND_IMAGE_PATH)
    st.markdown("""
        <style>
        .login-form {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 2rem;
            border-radius: 10px;
            max-width: 400px;
            margin: auto;
            margin-top: 100px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>AI Inventory Manager</h2>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_login(username, password):
                st.session_state.logged_in = True
            else:
                st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)

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
    fig1 = px.bar(df.groupby("category")["quantity"].sum().reset_index(),
                  x="category", y="quantity", color="category",
                  title="Total Quantity per Category")
    st.plotly_chart(fig1, use_container_width=True)

    st.write("### Stock Value by Supplier")
    df["stock_value"] = df["quantity"] * df["price"]
    fig2 = px.pie(df, names="supplier", values="stock_value", title="Stock Value Distribution by Supplier")
    st.plotly_chart(fig2, use_container_width=True)

    st.write("### Download Data")
    excel = convert_df_to_excel(df)
    st.download_button("Download Excel", data=excel, file_name="inventory.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    csv = convert_df_to_csv(df)
    st.download_button("Download CSV", data=csv, file_name="inventory.csv", mime="text/csv")

# --- Main Application ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        set_background(BACKGROUND_IMAGE_PATH)
        st.sidebar.title("Inventory Menu")
        choice = st.sidebar.radio("Choose Action", ["➕ Add Product", "📋 View Products", "✏️ Update Product", "❌ Delete Product", "📊 Dashboard", "🚪 Logout"])

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
            if df.empty:
                st.warning("No products available to update.")
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
                st.warning("No products available to delete.")
                return
            product_ids = df["id"].tolist()
            selected_id = st.selectbox("Select Product ID to Delete", product_ids)
            password = st.text_input("Enter Password to Confirm Deletion", type="password")
            if st.button("Delete Product"):
                if password == DELETE_PASSWORD:
                    delete_product(selected_id)
                    st.success("✅ Product deleted successfully!")
                else:
                    st.error("Incorrect password. Deletion aborted.")

        elif choice == "📊 Dashboard":
            show_dashboard()

        elif choice == "🚪 Logout":
            st.session_state.logged_in = False
            st.experimental_rerun()

# --- Run Application ---
if __name__ == "__main__":
    main()
