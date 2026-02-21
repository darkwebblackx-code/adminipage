import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# ---------------------------
# Config
# ---------------------------
st.set_page_config(page_title="Coty Admin Page", page_icon="🛒", layout="wide")

DB_NAME = "orders.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")  # Change in Render environment

# ---------------------------
# Automatic Database Creation
# ---------------------------
if not os.path.exists(DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        location TEXT NOT NULL,
        order_details TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        status TEXT DEFAULT 'Pending'
    )
    """)
    conn.commit()
    conn.close()
    print("✅ orders.db na table orders zimeundwa automatically")

# ---------------------------
# Session State for Login
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------------------
# Login Page
# ---------------------------
def login():
    st.title("🔐 Admin Login")
    password_input = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Password is incorrect. Try again!")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------------------
# Admin Page
# ---------------------------
st.title("🛒 Coty Admin Dashboard")
st.subheader("Order Details")

# Connect to database
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)

# ---------------------------
# Sound alert for new orders
# ---------------------------
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = len(df)

if len(df) > st.session_state.last_order_count:
    st.session_state.last_order_count = len(df)
    # Trigger alert sound
    st.audio("https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg")

# ---------------------------
# Display orders in table
# ---------------------------
st.dataframe(df)

# ---------------------------
# Download orders as CSV
# ---------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Orders as CSV",
    data=csv,
    file_name=f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# ---------------------------
# Delete orders
# ---------------------------
st.subheader("Delete Orders")
order_id_to_delete = st.number_input("Enter Order ID to Delete", min_value=1, step=1)
if st.button("Delete Order"):
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id=?", (order_id_to_delete,))
    conn.commit()
    st.success(f"✅ Order ID {order_id_to_delete} deleted")
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    st.dataframe(df)

conn.close()

# ---------------------------
# Communicate with AI (Optional)
# ---------------------------
st.subheader("Send Message to AI Chatbot")
ai_message = st.text_input("Message for AI")
if st.button("Send to AI"):
    # Here you would integrate your Gemini AI call, e.g.,
    # response = call_gemini(ai_message)
    response = f"Simulated AI Response: You said '{ai_message}'"
    st.success(response)
