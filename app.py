# admin.py - Coty Orders Admin Dashboard (Standalone)
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ================= DATABASE =====================
DB_NAME = "orders.db"  # Same database used by chatbot

# ================= STREAMLIT UI =================
st.set_page_config(page_title="Coty Admin Dashboard", page_icon="📊")
st.title("📊 Coty Orders Admin Panel")
st.sidebar.title("🔐 Admin Panel")

# ================= ADMIN LOGIN ==================
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")
admin_password_input = st.sidebar.text_input("Weka Admin Password", type="password")

if admin_password_input != ADMIN_PASSWORD:
    st.warning("⚠️ Tafadhali weka password sahihi ili kuingia.")
    st.stop()

st.sidebar.success("✅ Umeingia Admin")

# ================= LOAD ORDERS ==================
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
conn.close()

if df.empty:
    st.info("Hakuna orders bado.")
else:
    # ================= ORDER STATS =================
    st.subheader("📈 Order Statistics")
    total_orders = len(df)
    today_orders = len(df[df["created_at"].str.contains(datetime.now().strftime("%Y-%m-%d"))])
    col1, col2 = st.columns(2)
    col1.metric("Total Orders", total_orders)
    col2.metric("Orders Today", today_orders)

    st.markdown("---")

    # ================= ORDERS TABLE =================
    st.subheader("📋 Orders List")
    st.dataframe(df, use_container_width=True)

    # ================= DOWNLOAD CSV =================
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Orders CSV", data=csv, file_name="coty_orders.csv", mime="text/csv")

    st.markdown("---")

    # ================= DELETE ORDER =================
    st.subheader("🗑️ Delete Order")
    order_id_to_delete = st.number_input("Weka Order ID ya kufuta", min_value=1, step=1)
    if st.button("Futa Order"):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM orders WHERE id = ?", (order_id_to_delete,))
        conn.commit()
        conn.close()
        st.success(f"Order ID {order_id_to_delete} imefutwa. Refresh page.")
