import streamlit as st
import sqlite3
import os
from google import genai

st.title("🛒 Coty Admin Dashboard")

# --- Database ---
conn = sqlite3.connect("orders.db", check_same_thread=False)
cursor = conn.cursor()

# --- API ---
API_KEY = os.environ.get("GEMINI_API_KEY_RENDER")
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash"

# --- Show Orders ---
st.subheader("Order Details")
cursor.execute("SELECT * FROM orders ORDER BY id DESC")
orders = cursor.fetchall()
if not orders:
    st.info("Hakuna order bado.")
else:
    for order in orders:
        st.markdown(f"""
**Order ID:** {order[0]}  
**Jina:** {order[1]}  
**Simu:** {order[2]}  
**Location:** {order[3]}  
**Bidhaa:** {order[4]}  
**Idadi:** {order[5]}
""")
        st.divider()

# --- Delete Orders ---
st.subheader("Delete Order")
delete_id = st.number_input("Enter Order ID to delete", min_value=1, step=1)
if st.button("Delete Order"):
    cursor.execute("SELECT * FROM orders WHERE id=?", (delete_id,))
    check = cursor.fetchone()
    if check:
        cursor.execute("DELETE FROM orders WHERE id=?", (delete_id,))
        conn.commit()
        st.success(f"✅ Order ID {delete_id} deleted")
        st.experimental_rerun()
    else:
        st.error("❌ Order ID haipo")

# --- Send Message to AI ---
st.subheader("Send Message to AI")
admin_msg = st.text_area("Message for AI")

if st.button("Send to AI"):
    if admin_msg.strip()=="":
        st.error("Andika message kwanza")
    else:
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=admin_msg,
                config={"temperature":0.3}
            ).text
            st.success("AI Response:")
            st.write(response)
        except Exception as e:
            st.error(f"Kosa la AI: {e}")
