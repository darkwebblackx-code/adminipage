# app.py - Coty AI Chatbot + Admin Panel
# Hakikisha hii ina root ya repo, sio folder ndani

import streamlit as st
import os
from google import genai
from google.genai.errors import APIError
import sqlite3
from datetime import datetime
import pandas as pd

# =====================================================
# ================= DATABASE SETUP ===================
# =====================================================
DB_NAME = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            location TEXT,
            order_details TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_order(name, phone, location, details):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (customer_name, phone, location, order_details, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, location, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# =====================================================
# ================= GEMINI AI SETUP ==================
# =====================================================
RENDER_ENV_VAR_NAME = "GEMINI_API_KEY_RENDER"

try:
    API_KEY = os.environ.get(RENDER_ENV_VAR_NAME)
    if not API_KEY:
        st.error(f"❌ Gemini API Key haijapatikana. Weka Environment Variable: '{RENDER_ENV_VAR_NAME}'")
        st.stop()

    @st.cache_resource
    def initialize_gemini_client(api_key):
        return genai.Client(api_key=api_key)

    client = initialize_gemini_client(API_KEY)

except Exception as e:
    st.error(f"Kosa wakati wa kuunganisha Gemini: {e}")
    st.stop()

GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
Wewe ni **Coty**, mhudumu wa wateja wa kidigitali mwenye **uwezo na akili mnemba (AI)**...
# (weka SYSTEM_PROMPT yako yote kama ilivyo)
"""

# =====================================================
# ================= STREAMLIT UI =====================
# =====================================================
st.set_page_config(page_title="Aura Chatbot (Gemini Powered)", page_icon="✨")
st.title("Karibu Coty Butchery")
st.caption("Huduma ya haraka zaidi ya kidigitali!")

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "customer_data" not in st.session_state:
    st.session_state.customer_data = {"name": None, "phone": None, "location": None}

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Uliza swali lako hapa"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare conversation for Gemini
    gemini_contents = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
        for m in st.session_state.messages
    ]

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_completion = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=gemini_contents,
                    config={"system_instruction": SYSTEM_PROMPT, "temperature": 0.8}
                )
                response = chat_completion.text
                st.markdown(response)

    except APIError as e:
        response = f"Nakuomba radhi, Gemini ina changamoto (API Error). Kosa: {e}"
        st.markdown(response)

    except Exception as e:
        response = f"Samahani, kosa lisilotarajiwa: {e}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # Detect order keywords automatically
    order_keywords = ["naagiza", "weka oda", "delivery", "nitachukua", "nakubali"]
    if any(word in prompt.lower() for word in order_keywords):
        name = st.session_state.customer_data.get("name") or "Haijajulikana"
        phone = st.session_state.customer_data.get("phone") or "Haijajulikana"
        location = st.session_state.customer_data.get("location") or "Haijajulikana"
        save_order(name, phone, location, prompt)

# =====================================================
# ================= ADMIN PANEL ======================
# =====================================================
st.sidebar.markdown("---")
st.sidebar.title("🔐 Admin Panel")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")
admin_password_input = st.sidebar.text_input("Weka Admin Password", type="password")

if admin_password_input == ADMIN_PASSWORD:
    st.sidebar.success("Umeingia Admin")
    st.title("📊 Coty Orders Dashboard")

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()

    if df.empty:
        st.info("Hakuna orders bado.")
    else:
        # Order stats
        st.subheader("📈 Order Statistics")
        total_orders = len(df)
        today_orders = len(df[df["created_at"].str.contains(datetime.now().strftime("%Y-%m-%d"))])
        col1, col2 = st.columns(2)
        col1.metric("Total Orders", total_orders)
        col2.metric("Orders Today", today_orders)

        st.markdown("---")

        # Orders table
        st.subheader("📋 Orders List")
        st.dataframe(df, use_container_width=True)

        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")
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
