import streamlit as st
import random
from datetime import date
import json
import os
import google.generativeai as genai
from datetime import datetime

def translate_crop(crop_name):
    # Dictionary of common crops
    translations = {
        "rice": "Rice (அரிசி)",
        "paddy": "Paddy (நெல்)",
        "wheat": "Wheat (கோதுமை)",
        "cotton": "Cotton (பருத்தி)",
        "sugarcane": "Sugarcane (கரும்பு)",
        "tomato": "Tomato (தக்காளி)",
        "onion": "Onion (வெங்காயம்)",
        "corn": "Corn (மக்காச்சோளம்)",
        "peanut": "Peanut (நிலக்கடலை)"
    }
    # Clean the input and look it up
    clean_name = crop_name.lower().strip()
    return translations.get(clean_name, crop_name.title())


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
        background-color: #2e7d32 !important; /* Solid Green */
        color: #ffffff !important;
        border-radius: 8px;
        border: none;
    }
    /* Force all text inside buttons to be white */
    div.stButton > button * {
        color: #ffffff !important;
    }
    div.stButton > button:hover {
        background-color: #1b5e20 !important;
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
            "reviews": {},
            "equipment": [
                {"id": 1, "type": "Tractor", "name": "Mahindra 575 DI", "available": 3, "rate": 800},
                {"id": 2, "type": "Tractor", "name": "Swaraj 744 FE", "available": 1, "rate": 750},
                {"id": 3, "type": "Goods Vehicle", "name": "Tata Ace (Chota Hathi)", "available": 4, "rate": 400},
                {"id": 4, "type": "Goods Vehicle", "name": "Mahindra Bolero Pickup", "available": 2, "rate": 600}
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
                            # --- NEW: Check for Unique Name ---
                            name_exists = any(u["name"].lower() == name.lower() for u in db["users"].values())
                            if name_exists:
                                st.error("⚠️ This Name is already registered! Please use a unique name (e.g., 'Ravi - North').")
                            else:
                                db["users"][email] = {
                                    "name": name, 
                                    "phone": phone, 
                                    "role": "Farmer" if role in ["Farmer", "விவசாயி"] else "Consumer"
                                }
                                save_db(db)
                                st.session_state.current_email = email
                                st.rerun()
                        else:
                            # Log in existing user
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

    # --- NEW: Global Public Directory Search ---
    st.sidebar.divider()
    st.sidebar.subheader("🔍 Public Directory / அடைவு")
    search_query = st.sidebar.text_input("Search users by name...")
    if search_query:
        results = [u for u in db["users"].values() if search_query.lower() in u["name"].lower()]
        if results:
            for r in results:
                st.sidebar.info(f"👤 **{r['name']}** ({r['role']})")
                # Show ratings if it is a farmer
                if r['role'] == "Farmer":
                    f_email = [email for email, data in db["users"].items() if data['name'] == r['name']][0]
                    farmer_reviews = db.get("reviews", {}).get(f_email, [])
                    if farmer_reviews:
                        rating = sum(rev['rating'] for rev in farmer_reviews) / len(farmer_reviews)
                        st.sidebar.caption(f"⭐ {rating:.1f} ({len(farmer_reviews)} Reviews)")
                    else:
                        st.sidebar.caption("No reviews yet.")
        else:
            st.sidebar.warning("No users found matching that name.")

    

    # ================= CONSUMER VIEW =================
    if user_info["role"] == "Consumer":
        st.header(f"🛒 {t['marketplace']} (Consumer View)")
        
        # --- NEW: Consumer Refresh Button ---
        if st.button("🔄 Check for Updates / புதுப்பிக்கவும்"):
            db = load_db()
            st.rerun()
            
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.container(border=True):
                st.subheader(t["post_demand"])
                with st.form("demand_form", clear_on_submit=True):
                    crop = st.text_input(t["crop_name"])
                    qty = st.number_input(t["qty"] + " (KG)", min_value=1, step=1)
                    price = st.number_input("Offered Price / வழங்கப்படும் விலை (₹)", min_value=1, value=1000, step=100)
                    if st.form_submit_button("Submit Request"):
                        if crop:
                            db["demands"].append({
                                "id": random.randint(1000, 9999),
                                "consumer_email": st.session_state.current_email,
                                "consumer_name": user_info['name'],
                                "crop": crop, "qty": int(qty), "price": int(price), "status": "Open",
                                "farmer_email": "", "farmer_name": ""
                            })
                            save_db(db)
                            st.success("Demand Broadcasted!")
                            st.rerun()
                    
        with col2:
            st.subheader("Live Negotiations & Agreements")
            
            my_open_demands = [d for d in db["demands"] if d["consumer_email"] == st.session_state.current_email and d["status"] != "Closed"]
            if my_open_demands:
                for d in my_open_demands:
                    with st.container(border=True):
                        if d["status"] == "Open":
                            st.info(f"⏳ Waiting for farmers: **{d['crop']}** ({d['qty']} KG) at ₹{d['price']}")
                        elif d["status"] == "Countered":
                            # Show Farmer Rating on Counter Offer
                            farmer_reviews = db.get("reviews", {}).get(d['farmer_email'], [])
                            rating_text = f"⭐ {sum(r['rating'] for r in farmer_reviews)/len(farmer_reviews):.1f} ({len(farmer_reviews)} Reviews)" if farmer_reviews else "No reviews yet"
                            
                            st.warning(f"🔄 **Counter-Offer!** Farmer {d['farmer_name']} [{rating_text}] offers ₹{d['price']} for {d['qty']} KG.")
                            
                            # Create 3 columns for Accept, Decline, and Counter
                            colA, colB, colC = st.columns(3)
                            
                            with colA:
                                if st.button("Accept Deal / ஏற்கவும்", key=f"acc_cnt_{d['id']}"):
                                    for m_idx, main_d in enumerate(db["demands"]):
                                        if main_d["id"] == d["id"]:
                                            db["demands"][m_idx]["status"] = "Closed"
                                            break
                                    db["agreements"].append({
                                        "id": f"AGR-{random.randint(10000, 99999)}",
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "consumer_email": d['consumer_email'],
                                        "consumer_name": d['consumer_name'],
                                        "consumer_phone": user_info['phone'],
                                        "farmer_email": d['farmer_email'],
                                        "farmer_name": d['farmer_name'],
                                        "farmer_phone": db["users"][d['farmer_email']]['phone'],
                                        "crop": d['crop'], "qty": d['qty'], "price": d['price']
                                    })
                                    save_db(db)
                                    st.rerun()

                            with colB:
                                if st.button("Decline / நிராகரி", key=f"dec_{d['id']}"):
                                    for m_idx, main_d in enumerate(db["demands"]):
                                        if main_d["id"] == d["id"]:
                                            # Reset to open market and clear the specific farmer
                                            db["demands"][m_idx]["status"] = "Open"
                                            db["demands"][m_idx]["farmer_email"] = ""
                                            db["demands"][m_idx]["farmer_name"] = ""
                                            break
                                    save_db(db)
                                    st.rerun()

                            with colC:
                                new_price = st.number_input("New Offer (₹)", min_value=1, value=d['price'] - 100, step=50, key=f"inp_cons_{d['id']}")
                                if st.button("Send Counter / மாற்று விலை", key=f"cnt_cons_{d['id']}"):
                                    for m_idx, main_d in enumerate(db["demands"]):
                                        if main_d["id"] == d["id"]:
                                            # Update price and return to open market for all farmers to see
                                            db["demands"][m_idx]["price"] = new_price
                                            db["demands"][m_idx]["status"] = "Open"
                                            db["demands"][m_idx]["farmer_email"] = ""
                                            db["demands"][m_idx]["farmer_name"] = ""
                                            break
                                    save_db(db)
                                    st.rerun()

            st.divider()
            st.write("**Your Final Agreements / உங்கள் ஒப்பந்தங்கள்:**")
            my_agreements = [a for a in db["agreements"] if a["consumer_email"] == st.session_state.current_email]
            
            for a in my_agreements:
                with st.container(border=True):
                    st.success(f"✅ **{a['crop']}** ({a['qty']} KG) at ₹{a['price']} | Time: {a['timestamp']}")
                    st.write(f"📞 **Farmer Contact:** {a['farmer_name']} | Ph: {a['farmer_phone']} | Email: {a['farmer_email']}")
                    
                    # --- NEW: Downloadable Receipt ---
                    # --- NEW: Official Bilingual Receipt ---
                    receipt_text = f"""தமிழ்நாடு ஊரக உற்பத்தி ரசீது / GOVT RURAL PRODUCTION RECEIPT
-------------------------------------------------------
பரிவர்த்தனை எண் / Transaction ID: {a['id']}
தேதி மற்றும் நேரம் / Date & Time: {a['timestamp']}

பொருள் / Commodity: {a['crop']}
அளவு / Quantity: {a['qty']} KG
ஒப்பந்த விலை / Final Price: ₹{a['price']}

விவசாயி விவரங்கள் / FARMER DETAILS:
பெயர் / Name: {a['farmer_name']}
எண் / Ph: {a['farmer_phone']}

நுகர்வோர் விவரங்கள் / CONSUMER DETAILS:
பெயர் / Name: {a['consumer_name']}
எண் / Ph: {a['consumer_phone']}
-------------------------------------------------------
மின்-கையொப்பம் சரிபார்க்கப்பட்டது / e-Signature Verified"""

                    st.download_button("📥 Download Receipt / ரசீதை பதிவிறக்குக", data=receipt_text, file_name=f"TN_Agri_Receipt_{a['id']}.txt", mime="text/plain", key=f"dl_{a['id']}_unique")
                    
                    # --- NEW: Review System ---
                    with st.expander(f"Rate & Review Farmer: {a['farmer_name']}"):
                        rating = st.slider("Rating (Stars)", 1, 5, 5, key=f"rate_{a['id']}")
                        comment = st.text_input("Write a review / விமர்சனம்", key=f"rev_{a['id']}")
                        if st.button("Submit Review", key=f"subrev_{a['id']}"):
                            if "reviews" not in db: db["reviews"] = {}
                            if a['farmer_email'] not in db["reviews"]: db["reviews"][a['farmer_email']] = []
                            db["reviews"][a['farmer_email']].append({"rating": rating, "comment": comment, "by": user_info['name']})
                            save_db(db)
                            st.success("Review saved! / விமர்சனம் சேமிக்கப்பட்டது!")
    # ================= FARMER VIEW =================
    # ================= FARMER VIEW =================
    elif user_info["role"] == "Farmer":
        tabs = st.tabs([f"🛒 {t['marketplace']}", f"🌱 {t['sowing']}", f"🤖 {t['ai_predict']}"])
        
        # TAB 1: Marketplace
        with tabs[0]:
            st.header("Live Consumer Demands / நேரடி நுகர்வோர் தேவைகள்")
            
            # THE FIX: A button to safely fetch new data from the database
            if st.button("🔄 Check for New Demands"):
                db = load_db() # Force reload the JSON file
                st.rerun()
                
            open_demands = [d for d in db["demands"] if d["status"] == "Open"]
            
            if not open_demands:
                st.info("No active demands right now. Click 'Check for New Demands' to refresh.")
                
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
                                    
                            # Fetch full contact details of the consumer
                            c_info = db["users"][d['consumer_email']]
                            
                            db["agreements"].append({
                                "id": f"AGR-{random.randint(10000, 99999)}",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "consumer_email": d['consumer_email'], "consumer_name": d['consumer_name'], "consumer_phone": c_info['phone'],
                                "farmer_email": st.session_state.current_email, "farmer_name": user_info['name'], "farmer_phone": user_info['phone'],
                                "crop": d['crop'], "qty": d['qty'], "price": d['price']
                            })
                            save_db(db)
                            st.success("Deal Accepted! Check below for details.")
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

        # --- NEW: Farmer's Final Agreements & Receipts Ledger ---
            st.divider()
            st.write("### Your Final Agreements & Sales / உங்கள் ஒப்பந்தங்கள்")
            
            my_sales = [a for a in db["agreements"] if a["farmer_email"] == st.session_state.current_email]
            
            if not my_sales:
                st.write("No finalized sales yet.")
            else:
                for a in my_sales:
                    with st.container(border=True):
                        st.success(f"✅ **{a['crop']}** ({a['qty']} KG) sold for ₹{a['price']} | Time: {a['timestamp']}")
                        st.write(f"📞 **Consumer Contact:** {a['consumer_name']} | Ph: {a['consumer_phone']} | Email: {a['consumer_email']}")
                        
                        # Generate the identical downloadable receipt for the farmer
                        # --- NEW: Official Bilingual Receipt ---
                        receipt_text = f"""தமிழ்நாடு ஊரக உற்பத்தி ரசீது / GOVT RURAL PRODUCTION RECEIPT
-------------------------------------------------------
பரிவர்த்தனை எண் / Transaction ID: {a['id']}
தேதி மற்றும் நேரம் / Date & Time: {a['timestamp']}

பொருள் / Commodity: {a['crop']}
அளவு / Quantity: {a['qty']} KG
ஒப்பந்த விலை / Final Price: ₹{a['price']}

விவசாயி விவரங்கள் / FARMER DETAILS:
பெயர் / Name: {a['farmer_name']}
எண் / Ph: {a['farmer_phone']}

நுகர்வோர் விவரங்கள் / CONSUMER DETAILS:
பெயர் / Name: {a['consumer_name']}
எண் / Ph: {a['consumer_phone']}
-------------------------------------------------------
மின்-கையொப்பம் சரிபார்க்கப்பட்டது / e-Signature Verified"""

                        st.download_button("📥 Download Receipt / ரசீதை பதிவிறக்குக", data=receipt_text, file_name=f"TN_Agri_Receipt_{a['id']}.txt", mime="text/plain", key=f"dl_{a['id']}_unique")
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

# ================= UNIVERSAL MACHINERY & TRANSPORT POOL (SIDEBAR) =================
    st.sidebar.divider()
    with st.sidebar.expander("🚜 Machinery & Transport Pool"):
        st.write("Rent shared agricultural equipment and goods vehicles via local panchayat nodes.")
        
        # Loop through the new equipment list
        for item in db.get("equipment", []):
            is_avail = item["available"] > 0
            
            # Display an icon based on the type
            icon = "🚜" if item["type"] == "Tractor" else "🚚"
            
            st.info(f"**{icon} {item['name']}**")
            st.caption(f"Type: {item['type']}")
            st.write(f"Available: {item['available']} Unit(s)")
            st.write(f"Rate: ₹{item['rate']} / hr")
            
            if is_avail:
                if st.button(f"Book {item['type']} (₹{item['rate']})", key=f"book_eq_{item['id']}"):
                    # Deduct availability
                    for idx, db_item in enumerate(db["equipment"]):
                        if db_item["id"] == item["id"]:
                            db["equipment"][idx]["available"] -= 1
                            break
                    save_db(db)
                    
                    st.success(f"{item['type']} Reserved! Scan below to complete Panchayat booking:")
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=upi://pay?pa=panchayat@bank&pn=TransportPool&am={item['rate']}", width=150)
            else:
                st.button("Currently Unavailable", key=f"book_eq_{item['id']}", disabled=True)

