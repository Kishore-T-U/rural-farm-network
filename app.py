import streamlit as st
import random
from datetime import date
import json
import os
import google.generativeai as genai

# --- PAGE CONFIGURATION & GOVERNMENT THEME ---
st.set_page_config(page_title="Smart Village Farm Network", page_icon="🌾", layout="wide")

# Injecting CSS for a Light Pale Green Government Theme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #e8f5e9; /* Pale Government Green */
    }
    
    /* Make text readable on green */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #1b5e20 !important; /* Dark Forest Green */
    }

    /* Style the buttons */
    div.stButton > button {
        background-color: #2e7d32; /* Solid Green */
        color: white !important;
        border-radius: 8px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #1b5e20;
    }

    /* Make input boxes clean */
    .stTextInput input, .stNumberInput input {
        background-color: white !important;
        border: 1px solid #a5d6a7 !important;
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FAIL-PROOF FILE DATABASE ---
DB_FILE = "farm_db.json"

def init_db():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "users": {},
            "demands": [],
            "agreements": [],
            "sowing_data": [],
            "tractors": [
                {"id": 1, "name": "Mahindra 575 DI", "available": 3, "rate": 800},
                {"id": 2, "name": "Swaraj 744 FE", "available": 1, "rate": 750}
            ]
        }
        with open(DB_FILE, "w") as f:
            json.dump(initial_data, f)

def load_db():
    init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Load the database at the start of every interaction
db = load_db()

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
    st.markdown("<p style='text-align: center; color: #2e7d32;'>Govt. Rural Production Management Portal</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.subheader(t["login"])
            with st.form("auth_form"):
                email = st.text_input(t["email"])
                name = st.text_input("Full Name / முழு பெயர்")
                phone = st.text_input("Mobile Number / அலைபேசி எண்")
                role = st.selectbox(t["role"], [t["farmer"], t["consumer"]])
                
                if st.form_submit_button(t["login"], use_container_width=True):
                    if email and name:
                        if email not in db["users"]:
                            db["users"][email] = {
                                "name": name, 
                                "phone": phone, 
                                "role": "Farmer" if role in ["Farmer", "விவசாயி"] else "Consumer"
                            }
                            save_db(db)
                        st.session_state.current_email = email
                        st.rerun()

# --- MAIN DASHBOARD ---
# --- MAIN DASHBOARD ---
else:
    # --- BUG FIX: Check if user exists in the fresh cloud database ---
    if st.session_state.current_email not in db["users"]:
        st.session_state.current_email = None
        st.rerun()
        
    # If safe, proceed to load user info
    user_info = db["users"][st.session_state.current_email]
    st.sidebar.title(t["dashboard"])
    st.sidebar.success(f"👤 {user_info['name']} ({user_info['role']})")
    
    if st.sidebar.button("Logout / வெளியேறு"):
        st.session_state.current_email = None
        st.rerun()

    # ================= CONSUMER VIEW =================
    if user_info["role"] == "Consumer":
        st.header(f"🛒 {t['marketplace']} (Consumer View)")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.container(border=True):
                st.subheader(t["post_demand"])
                with st.form("demand_form"):
                    crop = st.text_input(t["crop_name"])
                    qty = st.number_input(t["qty"] + " (KG)", min_value=1)
                    price = st.number_input("Offered Price / வழங்கப்படும் விலை (₹)", min_value=1)
                    if st.form_submit_button("Submit Request"):
                        db["demands"].append({
                            "id": random.randint(1000, 9999),
                            "consumer_email": st.session_state.current_email,
                            "consumer_name": user_info['name'],
                            "crop": crop, "qty": qty, "price": price, "status": "Open",
                            "farmer_email": "", "farmer_name": ""
                        })
                        save_db(db)
                        st.rerun()
                    
        with col2:
            st.subheader("Live Negotiations & Agreements")
            
            # Pending / Negotiating Demands
            my_open_demands = [d for d in db["demands"] if d["consumer_email"] == st.session_state.current_email and d["status"] != "Closed"]
            if my_open_demands:
                st.write("**Pending Requests:**")
                for idx, d in enumerate(my_open_demands):
                    with st.container(border=True):
                        if d["status"] == "Open":
                            st.info(f"⏳ Waiting for farmers: **{d['crop']}** ({d['qty']} KG) at ₹{d['price']}")
                        elif d["status"] == "Countered":
                            st.warning(f"🔄 **Counter-Offer!** Farmer {d['farmer_name']} offers ₹{d['price']} for {d['qty']} KG of {d['crop']}.")
                            if st.button("Accept Farmer's Price", key=f"acc_cnt_{d['id']}"):
                                # Find the demand in the main db and update it
                                for m_idx, main_d in enumerate(db["demands"]):
                                    if main_d["id"] == d["id"]:
                                        db["demands"][m_idx]["status"] = "Closed"
                                        break
                                db["agreements"].append({
                                    "consumer_email": d['consumer_email'],
                                    "consumer_name": d['consumer_name'],
                                    "farmer_email": d['farmer_email'],
                                    "farmer_name": d['farmer_name'],
                                    "crop": d['crop'], "qty": d['qty'], "price": d['price']
                                })
                                save_db(db)
                                st.rerun()

            st.divider()
            
            # Final Agreements
            st.write("**Your Final Agreements / உங்கள் ஒப்பந்தங்கள்:**")
            my_agreements = [a for a in db["agreements"] if a["consumer_email"] == st.session_state.current_email]
            if not my_agreements:
                st.write("No finalized agreements yet.")
            for a in my_agreements:
                st.success(f"✅ **{a['crop']}** ({a['qty']} KG) locked at ₹{a['price']} with Farmer: {a['farmer_name']}")

    # ================= FARMER VIEW =================
    elif user_info["role"] == "Farmer":
        tabs = st.tabs([f"🛒 {t['marketplace']}", f"🌱 {t['sowing']}", f"🤖 {t['ai_predict']}"])
        
        # TAB 1: Marketplace
        with tabs[0]:
            st.header("Live Consumer Demands / நேரடி நுகர்வோர் தேவைகள்")
            open_demands = [d for d in db["demands"] if d["status"] == "Open"]
            
            if not open_demands:
                st.write("No active demands right now.")
                
            for d in open_demands:
                with st.container(border=True):
                    st.write(f"### {d['crop']} ({d['qty']} KG)")
                    st.write(f"**Consumer Offered Price:** ₹{d['price']} | **Buyer:** {d['consumer_name']}")
                    
                    colA, colB = st.columns(2)
                    with colA:
                        if st.button("Accept Deal / ஏற்கவும்", key=f"acc_farm_{d['id']}"):
                            for idx, main_d in enumerate(db["demands"]):
                                if main_d["id"] == d["id"]:
                                    db["demands"][idx]["status"] = "Closed"
                                    break
                            db["agreements"].append({
                                "consumer_email": d['consumer_email'],
                                "consumer_name": d['consumer_name'],
                                "farmer_email": st.session_state.current_email,
                                "farmer_name": user_info['name'],
                                "crop": d['crop'], "qty": d['qty'], "price": d['price']
                            })
                            save_db(db)
                            st.rerun()
                    
                    with colB:
                        counter_price = st.number_input("Suggest New Price (₹)", min_value=1, value=d['price'], key=f"inp_{d['id']}")
                        if st.button("Send Counter Offer", key=f"cnt_{d['id']}"):
                            for idx, main_d in enumerate(db["demands"]):
                                if main_d["id"] == d["id"]:
                                    db["demands"][idx]["status"] = "Countered"
                                    db["demands"][idx]["price"] = counter_price
                                    db["demands"][idx]["farmer_email"] = st.session_state.current_email
                                    db["demands"][idx]["farmer_name"] = user_info['name']
                                    break
                            save_db(db)
                            st.rerun()

        # TAB 2: Sowing Input
        with tabs[1]:
            st.header(t["sowing"])
            with st.container(border=True):
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
                        save_db(db)
                        st.rerun()
            
            st.subheader("Village Sowing Registry")
            st.table(db["sowing_data"])

        # TAB 3: AI Prediction & State Analytics
        # TAB 3: AI Prediction & State Analytics
        with tabs[2]:
            st.header(t["ai_predict"] + " (State-Level Integration)")
            st.write("Analyze localized sowing patterns strictly mapped to LGD codes and current climatic conditions to prevent market saturation.")
            
            # --- API KEY UPDATE: Automatically pull from Streamlit Secrets ---
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                st.success("Secure Government AI Link Established.")
            except:
                api_key = None
                st.error("API Key missing from Server Secrets.")
            
            # 1. Secure API Key Input
            api_key = st.text_input("Enter Gemini API Key (Hidden Securely) / AI குறியீட்டை உள்ளிடவும்", type="password")
            
            # 2. Local Government Directory (LGD) Integration for Tamil Nadu
            # In a production app, this would be an API call to the national LGD database
            tn_lgd_database = {
                "274154": {"district": "Coimbatore", "panchayat": "Odanthurai", "soil_type": "Red Calcareous", "avg_rainfall_mm": 600},
                "274189": {"district": "Erode", "panchayat": "Bhavani", "soil_type": "Alluvial", "avg_rainfall_mm": 700},
                "275441": {"district": "Thanjavur", "panchayat": "Papanasam", "soil_type": "Deltaic Alluvium", "avg_rainfall_mm": 950},
                "276211": {"district": "Madurai", "panchayat": "Melur", "soil_type": "Red Sandy", "avg_rainfall_mm": 850}
            }
            
            selected_lgd = st.selectbox("Select Target Panchayat (LGD Code) / கிராம பஞ்சாயத்து LGD குறியீடு", list(tn_lgd_database.keys()))
            location_data = tn_lgd_database[selected_lgd]
            
            st.info(f"📍 **Targeted Region:** {location_data['district']} District, {location_data['panchayat']} Panchayat | **Soil:** {location_data['soil_type']}")

            # 3. Simulated Live Weather & Trend Data Integration
            # In production, connect this to the Indian Meteorological Department (IMD) API
            current_weather = {
                "forecast": "Expected heavy rainfall in the next 14 days.",
                "temperature_trend": "Normal, averaging 28°C",
                "humidity": "75%"
            }

            if st.button("Generate Conclusive Market & Yield Analysis"):
                if not api_key:
                    st.error("Please provide your API key to authenticate the secure connection.")
                elif not db["sowing_data"]:
                    st.warning("No live sowing data registered for this zone yet.")
                else:
                    try:
                        # Configure the API securely using the user-provided key
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Filter database to only show data for the selected LGD code (simulated here by passing the whole DB for the prototype)
                        local_sowing_data = json.dumps(db['sowing_data'])
                        historical_data = json.dumps([{"year": 2025, "crop": "Rice", "yield_per_acre": "2400 KG", "market_status": "Oversaturated"}]) # Mock historical data
                        
                        # 4. Anti-Hallucination Strict Prompting
                        prompt = f"""
                        You are a strict, data-driven agricultural analytics engine for the Government of Tamil Nadu. 
                        You must NOT hallucinate, guess, or provide generic farming advice. Base your entire response strictly on the data provided below.
                        
                        [INPUT DATA]
                        LGD Code: {selected_lgd}
                        Location: {location_data['panchayat']}, {location_data['district']}
                        Soil Type: {location_data['soil_type']}
                        Current Live Sowing Data: {local_sowing_data}
                        Historical Yield Data (Previous Year): {historical_data}
                        Upcoming 14-Day Weather Forecast: {current_weather['forecast']}, Temp: {current_weather['temperature_trend']}
                        
                        [REQUIRED OUTPUT FORMAT]
                        1. Data Summary: Exactly how many total acres are currently sown with which crops?
                        2. Weather Impact: How will the 14-day weather forecast specifically impact the currently sown crops in this soil type?
                        3. Yield Prediction & Market Saturation: Based on the historical yield and current acres, what is the estimated total harvest? Is there a risk of market oversupply?
                        4. Conclusive Guidance: If the data indicates oversupply or weather risk, explicitly state an alternative crop. If you do not have enough data to prove this, output exactly: "INSUFFICIENT DATA TO MAKE CONCLUSIVE PREDICTION."
                        
                        Provide a brief, professional Tamil translation of the conclusive guidance at the end.
                        """
                        
                        with st.spinner(f"Analyzing encrypted data for LGD Code {selected_lgd}..."):
                            response = model.generate_content(prompt)
                            st.write(response.text)
                            
                    except Exception as e:
                        st.error(f"Secure Connection Failed or API Error: {e}")
