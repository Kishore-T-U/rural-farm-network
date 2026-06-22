import streamlit as st
import random
from datetime import date
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Smart Village Farm Network", page_icon="🌾", layout="wide")

# --- GLOBAL DATABASE (Visible to all users) ---
# Using cache_resource allows data to be shared across multiple browser tabs/users
@st.cache_resource
def get_global_db():
    return {
        "users": {}, # Format: "email@test.com": {"name": "...", "role": "Farmer", "phone": "..."}
        "demands": [],
        "agreements": [],
        "sowing_data": [],
        "tractors": [
            {"id": 1, "name": "Mahindra 575 DI", "available": 3, "rate": 800},
            {"id": 2, "name": "Swaraj 744 FE", "available": 1, "rate": 750}
        ]
    }

db = get_global_db()

# --- BILINGUAL DICTIONARY (English / Tamil) ---
lang_dict = {
    "English": {
        "title": "🌾 Smart Village Farm Network",
        "login": "Login / Register",
        "email": "Email Address",
        "role": "Role",
        "farmer": "Farmer",
        "consumer": "Consumer",
        "dashboard": "Village Dashboard",
        "marketplace": "Marketplace",
        "sowing": "My Sowing Details",
        "ai_predict": "AI Crop Prediction",
        "post_demand": "Post a Demand",
        "crop_name": "Crop Name",
        "qty": "Quantity",
        "area": "Land Area (Acres)"
    },
    "தமிழ்": {
        "title": "🌾 கிராமப்புற விவசாய கட்டமைப்பு",
        "login": "உள்நுழை / பதிவு செய்",
        "email": "மின்னஞ்சல் முகவரி",
        "role": "பங்கு",
        "farmer": "விவசாயி",
        "consumer": "நுகர்வோர்",
        "dashboard": "கிராம டாஷ்போர்டு",
        "marketplace": "சந்தை",
        "sowing": "விதைப்பு விவரங்கள்",
        "ai_predict": "AI பயிர் கணிப்பு",
        "post_demand": "தேவையை பதிவிடவும்",
        "crop_name": "பயிரின் பெயர்",
        "qty": "அளவு",
        "area": "நிலப்பரப்பு (ஏக்கர்)"
    }
}

# --- SESSION STATE (Local to the user) ---
if 'current_email' not in st.session_state:
    st.session_state.current_email = None
if 'lang' not in st.session_state:
    st.session_state.lang = "English"

# Language Toggle
st.sidebar.selectbox("Language / மொழி", ["English", "தமிழ்"], key="lang")
t = lang_dict[st.session_state.lang]

# --- LOGIN / REGISTRATION SYSTEM ---
if st.session_state.current_email is None:
    st.markdown(f"<h1 style='text-align: center;'>{t['title']}</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader(t["login"])
        with st.form("auth_form"):
            email = st.text_input(t["email"])
            name = st.text_input("Full Name / முழு பெயர்")
            phone = st.text_input("Mobile Number / அலைபேசி எண்")
            role = st.selectbox(t["role"], [t["farmer"], t["consumer"]])
            
            if st.form_submit_button(t["login"], use_container_width=True):
                if email and name:
                    # Register user if they don't exist
                    if email not in db["users"]:
                        db["users"][email] = {
                            "name": name, 
                            "phone": phone, 
                            # Always store role in English logic internally, translate for UI
                            "role": "Farmer" if role in ["Farmer", "விவசாயி"] else "Consumer"
                        }
                    st.session_state.current_email = email
                    st.rerun()

# --- MAIN DASHBOARD (Role-Based) ---
else:
    user_info = db["users"][st.session_state.current_email]
    st.sidebar.title(t["dashboard"])
    st.sidebar.success(f"👤 {user_info['name']} ({user_info['role']})")
    
    if st.sidebar.button("Logout / வெளியேறு"):
        st.session_state.current_email = None
        st.rerun()

    # --- CONSUMER VIEW ---
    if user_info["role"] == "Consumer":
        st.header(f"🛒 {t['marketplace']} (Consumer View)")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader(t["post_demand"])
            with st.form("demand_form"):
                crop = st.text_input(t["crop_name"])
                qty = st.number_input(t["qty"] + " (KG)", min_value=1)
                price = st.number_input("Offered Price / வழங்கப்படும் விலை (₹)", min_value=1)
                if st.form_submit_button("Submit / சமர்ப்பி"):
                    db["demands"].append({
                        "id": random.randint(1000, 9999),
                        "consumer_email": st.session_state.current_email,
                        "consumer_name": user_info['name'],
                        "crop": crop, "qty": qty, "price": price, "status": "Open"
                    })
                    st.success("Demand Broadcasted to Farmers!")
                    st.rerun()
                    
        with col2:
            st.subheader("Your Agreements / உங்கள் ஒப்பந்தங்கள்")
            my_agreements = [a for a in db["agreements"] if a["consumer_email"] == st.session_state.current_email]
            for a in my_agreements:
                st.info(f"**{a['crop']}** ({a['qty']} KG) at ₹{a['price']} - Accepted by Farmer: {a['farmer_name']} (Ph: {a['farmer_phone']})")

    # --- FARMER VIEW ---
    elif user_info["role"] == "Farmer":
        tabs = st.tabs([f"🌱 {t['sowing']}", f"🤖 {t['ai_predict']}", f"🛒 {t['marketplace']}"])
        
        # TAB 1: Sowing Input
        with tabs[0]:
            st.header(t["sowing"])
            with st.form("sowing_form"):
                s_crop = st.text_input(t["crop_name"])
                s_area = st.number_input(t["area"], min_value=0.1, step=0.5)
                s_amount = st.number_input("Seeds Amount (KG) / விதை அளவு", min_value=1)
                if st.form_submit_button("Save Details / சேமி"):
                    db["sowing_data"].append({
                        "farmer": user_info['name'],
                        "crop": s_crop,
                        "area": s_area,
                        "amount": s_amount
                    })
                    st.success("Data Recorded Successfully!")
                    st.rerun()
            
            st.subheader("Village Sowing Registry")
            st.table(db["sowing_data"])

        # TAB 2: AI Prediction Model
        with tabs[1]:
            st.header(t["ai_predict"])
            st.write("Analyze current village sowing data using AI to prevent market saturation and seed loss.")
            api_key = st.text_input("Enter AI API Key (Gemini) / AI குறியீட்டை உள்ளிடவும்", type="password")
            
            if st.button("Generate AI Market Analysis"):
                if not api_key:
                    st.error("Please provide an API key.")
                elif not db["sowing_data"]:
                    st.warning("No sowing data registered in the village yet.")
                else:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        prompt = f"""
                        You are an agricultural AI expert. Analyze this village's current sowing data:
                        {db['sowing_data']}
                        
                        1. Is there an overproduction risk for any specific crop?
                        2. What alternative crops should farmers plant instead to get better market value?
                        3. Provide the response clearly, summarizing the data first. Include a brief translation in Tamil at the end.
                        """
                        
                        with st.spinner("AI is analyzing local production data..."):
                            response = model.generate_content(prompt)
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"AI Model Error: {e}")

        # TAB 3: Marketplace (Accepting Demands)
        with tabs[2]:
            st.header("Live Consumer Demands / நேரடி நுகர்வோர் தேவைகள்")
            open_demands = [d for d in db["demands"] if d["status"] == "Open"]
            
            if not open_demands:
                st.write("No active demands right now.")
                
            for d in open_demands:
                with st.container(border=True):
                    st.write(f"### {d['crop']} ({d['qty']} KG)")
                    st.write(f"**Price:** ₹{d['price']} | **Consumer:** {d['consumer_name']}")
                    if st.button("Accept Agreement / ஒப்பந்தத்தை ஏற்கவும்", key=d['id']):
                        d["status"] = "Closed"
                        db["agreements"].append({
                            "consumer_email": d['consumer_email'],
                            "consumer_name": d['consumer_name'],
                            "farmer_email": st.session_state.current_email,
                            "farmer_name": user_info['name'],
                            "farmer_phone": user_info['phone'],
                            "crop": d['crop'], "qty": d['qty'], "price": d['price']
                        })
                        st.success("Agreement generated! Your contact info has been shared with the consumer.")
                        st.rerun()
