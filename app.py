import gradio as gr
import mysql.connector
import pandas as pd
import plotly.express as px
import base64  # for base64 encoding

# ---------- DB Connection ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Geetha$2500",
        database="inventory_db"
    )

# ---------- DB Functions ----------
def get_all_products():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM products", conn)
    conn.close()
    return df

def add_product(name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, quantity, price, supplier)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, category, quantity, price, supplier))
    conn.commit()
    conn.close()
    return "✅ Product added."

def update_product(id, name, category, quantity, price, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products SET name=%s, category=%s, quantity=%s, price=%s, supplier=%s
        WHERE id=%s
    """, (name, category, quantity, price, supplier, id))
    conn.commit()
    conn.close()
    return "✅ Product updated."

def delete_product(id, password):
    if password != "Dheeraj2500$":
        return "❌ Incorrect password"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return "✅ Product deleted"

def dashboard():
    df = get_all_products()
    if df.empty:
        return "No data to display", None, None
    
    fig1 = px.bar(df.groupby("category")["quantity"].sum().reset_index(),
                  x="category", y="quantity", color="category",
                  title="Total Quantity per Category")
    
    df["stock_value"] = df["quantity"] * df["price"]
    fig2 = px.pie(df, names="supplier", values="stock_value",
                  title="Stock Value by Supplier")
    
    return df, fig1, fig2

# ---------- Load your local images and convert to base64 ----------
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Replace these filenames with your actual image filenames
img_base64_login = get_base64_image("inven.jpg")
img_base64_main = get_base64_image("inven1.jpg")

# ---------- Custom CSS for login page ----------
custom_css_login = f"""
<style>
    /* Login Page Background */
    #login-page {{
        background-image: url("data:image/jpg;base64,{img_base64_login}");
        background-size: cover;
        background-attachment: fixed;
        color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.8);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    #login-page h2 {{
        color: #ffdd57;
        text-shadow: 1px 1px 3px #000;
    }}
    #login-page .gr-button {{
        background-color: #ff6f61 !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(255, 111, 97, 0.6);
        transition: background-color 0.3s ease;
    }}
    #login-page .gr-button:hover {{
        background-color: #ff3b2e !important;
        box-shadow: 0 6px 15px rgba(255, 59, 46, 0.8);
    }}
    #login-page .gr-textbox input {{
        color: white;
        background: rgba(255,255,255,0.15);
        border-radius: 8px;
        border: 1px solid #ff6f61;
        padding: 6px;
        outline: none;
    }}
</style>
"""

# ---------- Custom CSS for main app page ----------
custom_css_main = f"""
<style>
    /* Main App Background */
    #main-app {{
        background-image: url("data:image/jpg;base64,{img_base64_main}");
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 900px;
        margin: auto;
        box-shadow: 0 0 15px rgba(0,0,0,0.7);
    }}
    #main-app h1, #main-app h2, #main-app h3, #main-app h4 {{
        color: #ffdd57;
        text-shadow: 1px 1px 3px #000;
    }}
    #main-app .gr-button {{
        background-color: #ff6f61 !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(255, 111, 97, 0.6);
        transition: background-color 0.3s ease;
    }}
    #main-app .gr-button:hover {{
        background-color: #ff3b2e !important;
        box-shadow: 0 6px 15px rgba(255, 59, 46, 0.8);
    }}
    #main-app .gr-textbox, #main-app .gr-number {{
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
        border: 1px solid #ff6f61;
    }}
    #main-app .gr-textbox input, #main-app .gr-number input {{
        color: white;
        background: transparent;
        border: none;
        outline: none;
    }}
    #main-app .gr-dataframe {{
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        background-color: rgba(0,0,0,0.5);
        color: white;
    }}
    #main-app .gr-plot {{
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        background-color: rgba(0,0,0,0.5);
    }}
</style>
"""

# ---------- Login logic ----------
def verify_login(username, password):
    if username == "admin" and password == "Dheeraj2500$":
        return True, ""
    else:
        return False, "❌ Incorrect username or password"

# ---------- Gradio UI ----------
with gr.Blocks(title="AI Inventory Manager") as demo:
    # Inject CSS for both pages
    gr.HTML(custom_css_login)
    gr.HTML(custom_css_main)

    # Use State to keep track of login
    login_state = gr.State(False)

    # Assign IDs to columns for CSS scoping
    with gr.Column(visible=True, elem_id="login-page") as login_page:
        gr.Markdown("## 🔐 Login")
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_msg = gr.Textbox(label="Status", interactive=False)

    with gr.Column(visible=False, elem_id="main-app") as main_app:
        gr.Markdown("# 📦 AI Inventory Manager")

        with gr.Tabs():
            with gr.Tab("➕ Add Product"):
                with gr.Row():
                    name = gr.Textbox(label="Product Name")
                    category = gr.Textbox(label="Category")
                    quantity = gr.Number(label="Quantity", value=0)
                    price = gr.Number(label="Price", value=0.0)
                    supplier = gr.Textbox(label="Supplier")
                    submit = gr.Button("Add Product")
                output = gr.Textbox(label="Status", interactive=False)
                submit.click(add_product, inputs=[name, category, quantity, price, supplier], outputs=output)

            with gr.Tab("✏️ Update Product"):
                with gr.Row():
                    id_u = gr.Number(label="Product ID")
                    name_u = gr.Textbox(label="New Name")
                    category_u = gr.Textbox(label="New Category")
                    quantity_u = gr.Number(label="New Quantity")
                    price_u = gr.Number(label="New Price")
                    supplier_u = gr.Textbox(label="New Supplier")
                    update_btn = gr.Button("Update Product")
                update_out = gr.Textbox(label="Status", interactive=False)
                update_btn.click(update_product, inputs=[id_u, name_u, category_u, quantity_u, price_u, supplier_u], outputs=update_out)

            with gr.Tab("❌ Delete Product"):
                delete_id = gr.Number(label="Product ID")
                delete_pass = gr.Textbox(label="Admin Password", type="password")
                delete_btn = gr.Button("Delete Product")
                delete_out = gr.Textbox(label="Status", interactive=False)
                delete_btn.click(delete_product, inputs=[delete_id, delete_pass], outputs=delete_out)

            with gr.Tab("📋 View Products"):
                view_btn = gr.Button("Refresh Table")
                table = gr.Dataframe()
                view_btn.click(get_all_products, outputs=table)

            with gr.Tab("📊 Dashboard"):
                dash_btn = gr.Button("Show Dashboard")
                table_dash = gr.Dataframe()
                chart1 = gr.Plot()
                chart2 = gr.Plot()
                dash_btn.click(dashboard, outputs=[table_dash, chart1, chart2])

    # Login button click action
    def on_login_click(username, password):
        success, msg = verify_login(username, password)
        if success:
            return gr.update(visible=False), gr.update(visible=True), ""
        else:
            return gr.update(visible=True), gr.update(visible=False), msg

    login_button.click(
        on_login_click, 
        inputs=[username, password], 
        outputs=[login_page, main_app, login_msg]
    )

demo.launch()
