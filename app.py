import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ================= DATABASE =====================
DB_NAME = "orders.db"  # must match chatbot db

# ================= STREAMLIT UI =================
st.set_page_config(page_title="Coty Admin Dashboard", page_icon="📊")
st.title("📊 Coty Orders Admin Panel")

# ================= SESSION SETUP =================
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# ================= ADMIN LOGIN ==================
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234").strip()  # remove whitespace

if not st.session_state.admin_authenticated:
    st.subheader("🔐 Admin Login")
    
    with st.form("login_form"):
        password_input = st.text_input("Weka Admin Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if password_input == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("✅ Umeingia Admin!")
            else:
                st.error("❌ Password si sahihi. Jaribu tena.")
    
    st.stop()  # Stop execution until authenticated

# ================= LOAD ORDERS ==================
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
conn.close()

st.subheader("📋 Order Details")

if df.empty:
    st.info("Hakuna orders bado.")
else:
    # Format datetime
    df["Date"] = pd.to_datetime(df["created_at"]).dt.date
    df["Time"] = pd.to_datetime(df["created_at"]).dt.time
    df.rename(columns={
        "customer_name": "Customer Name",
        "phone": "Phone Number",
        "location": "Location",
        "order_details": "Order Details",
        "id": "Order ID"
    }, inplace=True)

    display_cols = ["Order ID", "Customer Name", "Phone Number", "Location", "Date", "Time", "Order Details"]
    st.dataframe(df[display_cols], use_container_width=True)

    # Download CSV
    csv = df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Orders CSV", data=csv, file_name="coty_orders.csv", mime="text/csv")

    st.markdown("---")

    # Delete order
    st.subheader("🗑️ Delete Order")
    order_id_to_delete = st.number_input("Weka Order ID ya kufuta", min_value=1, step=1)
    if st.button("Futa Order"):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM orders WHERE id = ?", (order_id_to_delete,))
        conn.commit()
        conn.close()
        st.success(f"Order ID {order_id_to_delete} imefutwa. Refresh page.")
