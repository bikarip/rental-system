import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse

# --- 1. EMAIL FUNCTION ---
def send_email_reminder(tenant_email, tenant_name, due_date, apartment):
    sender_email = "bikaprince9@gmail.com"       # Replace with your Gmail
    sender_password = "peys bxev cooz ldkd"   # Replace with your Google App Password
    
    subject = f"Rent Reminder - Apartment {apartment}"
    body = f"""
    Hello {tenant_name},
    
    This is a friendly reminder that your rent for Apartment {apartment} is due in 3 days on {due_date}.
    
    Please ensure your payment is made on time. Thank you!
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = tenant_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Connect to Gmail's SMTP server securely
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, tenant_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# --- 2. INITIALIZE DATABASE ---
conn = sqlite3.connect("rentals.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT NOT NULL,
        apartment_number TEXT NOT NULL,
        start_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        reminder_date TEXT NOT NULL,
        status TEXT DEFAULT 'Active'
    )
''')
conn.commit()

# --- 3. STREAMLIT UI: SIDEBAR (ADD CLIENT) ---
st.title("🏠 Apartment Rental & Reminder System")

st.sidebar.header("Add New Tenant")
name = st.sidebar.text_input("Tenant Name")
phone = st.sidebar.text_input("Phone Number(No spaces)")
email = st.sidebar.text_input("Email")
apartment = st.sidebar.text_input("Apartment Number")
start_date_input = st.sidebar.date_input("Lease Start Date", datetime.now())

if st.sidebar.button("Save Tenant"):
    if name and phone:
        start_date = start_date_input
        due_date = start_date + timedelta(days=30)
        reminder_date = due_date - timedelta(days=3)
        
        cursor.execute('''
            INSERT INTO clients (client_name, phone_number, email, apartment_number, start_date, due_date, reminder_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')
        ''', (name, phone, email, apartment, str(start_date), str(due_date), str(reminder_date)))
        conn.commit()
        st.sidebar.success(f"Tenant {name} added successfully!")
    else:
        st.sidebar.error("Please fill in at least the Name and Phone Number.")

# --- 4. STREAMLIT UI: MAIN DASHBOARD & ACTION BUTTONS ---
st.subheader("Current Active Tenants & Notifications")
cursor.execute("SELECT id, client_name, phone_number, email, apartment_number, due_date, reminder_date, status FROM clients")
rows = cursor.fetchall()

if not rows:
    st.info("No tenants found yet. Add one using the sidebar!")

for row in rows:
    tenant_id, name, phone, email, apt, due_date, reminder_date, status = row
    
    with st.expander(f"Tenant: {name} (Apt {apt}) - Status: {status}"):
        st.write(f"📞 **Phone:** {phone} | ✉️ **Email:** {email}")
        st.write(f"📅 **Due Date:** {due_date} | 🔔 **Reminder Date:** {reminder_date}")

        col1, col2 = st.columns(2)
        
       # Column 1: Send Email Reminder Button
        with col1:
            if st.button(f"Send Email", key=f"email_{tenant_id}"):
                if email:
                    success = send_email_reminder(email, name, due_date, apt)
                    if success:
                        st.success(f"Email sent to {name}!")
                    else:
                        st.error("Failed to send email. Check your Gmail App Password.")
                else:
                    st.warning("No email address saved for this tenant.")
                    
        # Column 2: Direct WhatsApp Click-to-Chat Link
        with col2:
            message_text = f"Hi {name}, friendly reminder that your rent for Apt {apt} is due in 3 days on {due_date}. Thank you!"
            encoded_message = urllib.parse.quote(message_text)
            whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
            
            st.markdown(f"[📲 Open WhatsApp for {name}]({whatsapp_url})", unsafe_allow_html=True)