import streamlit as st
import random
from datetime import date

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Smart Village Farm Network", page_icon="🌾", layout="wide")

# --- SESSION STATE INITIALIZATION (Simulating a Database) ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'tractors' not in st.session_state:
    st.session_state.tractors = [
        {"id": 1, "name": "Mahindra 575 DI SP Plus", "total": 3, "available": 3, "rate": 800},
        {"id": 2, "name": "Swaraj 744 FE", "total": 2, "available": 1, "rate": 750}
    ]
if 'demands' not in st.session_state:
    st.session_state.demands = []
if 'agreements' not in st.session_state:
    st.session_state.agreements = []

# --- LOGIN SCREEN ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center;'>🌾 Smart Village Farm Network</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Rural Production Management System</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Enter Your Email Address", placeholder="farmer@village.com")
            submitted = st.form_submit_button("Access System Portal", use_container_width=True)
            if submitted and email:
                st.session_state.user = email
                st.rerun()

# --- MAIN DASHBOARD ---
else:
    # Sidebar Navigation
    st.sidebar.title("🌾 Village Portal")
    st.sidebar.caption(f"Logged in as: {st.session_state.user}")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()
        
    st.sidebar.divider()
    menu = st.sidebar.radio("Navigation", ["🚜 Tractor Pooling", "🏪 Marketplace & Deals", "🌱 Predictive Sowing"])

    # --- SECTION 1: TRACTOR BOOKING ---
    if menu == "🚜 Tractor Pooling":
        st.header("Community Machinery Pool")
        st.write("Fair-recorded shared bookings handled via village service points.")
        
        # Add new tractor expander
        with st.expander("➕ Register New Tractor"):
            with st.form("add_tractor"):
                t_name = st.text_input("Model Name")
                col1, col2 = st.columns(2)
                t_count = col1.number_input("Total Inventory", min_value=1, step=1)
                t_rate = col2.number_input("Hourly Rental (₹)", min_value=100, step=50)
                if st.form_submit_button("Save Vehicle"):
                    st.session_state.tractors.append({"id": random.randint(100, 999), "name": t_name, "total": t_count, "available": t_count, "rate": t_rate})
                    st.rerun()

        st.divider()
        st.subheader("Available Machinery")
        
        cols = st.columns(3)
        for i, trac in enumerate(st.session_state.tractors):
            with cols[i % 3]:
                st.info(f"**{trac['name']}**")
                st.metric(label="Available Units", value=f"{trac['available']} / {trac['total']}")
                st.write(f"**Base Rate:** ₹{trac['rate']} / hour")
                
                if trac['available'] > 0:
                    if st.button(f"Book & Pay (₹{trac['rate']})", key=f"book_{trac['id']}"):
                        st.session_state.tractors[i]['available'] -= 1
                        # Show dummy QR Code
                        st.success("Tractor Booked! Please scan the QR code to complete payment.")
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=upi://pay?pa=village@bank&pn=TractorPool&am={trac['rate']}", width=150)
                else:
                    st.button("Currently Unavailable", key=f"book_{trac['id']}", disabled=True)

    # --- SECTION 2: MARKETPLACE ---
    elif menu == "🏪 Marketplace & Deals":
        st.header("Voluntary Collective Marketplace")
        st.write("Post demands, negotiate values, and issue binding transactional agreements.")
        
        col_form, col_feed = st.columns([1, 2])
        
        with col_form:
            st.subheader("Post a Demand")
            with st.form("demand_form"):
                d_crop = st.text_input("Crop Variety (e.g., Ponni Rice)")
                d_qty = st.text_input("Quantity (KG/Quintals)")
                d_price = st.number_input("Offered Price (₹ per unit)", min_value=1)
                d_del = st.text_area("Delivery Address")
                if st.form_submit_button("Broadcast Demand", use_container_width=True):
                    st.session_state.demands.append({
                        "id": random.randint(1000, 9999), "consumer": st.session_state.user, 
                        "crop": d_crop, "qty": d_qty, "price": d_price, "delivery": d_del, "status": "Open"
                    })
                    st.rerun()
                    
        with col_feed:
            st.subheader("Active Demands & Agreements")
            tab1, tab2 = st.tabs(["Live Market Feed", "Legal Agreements"])
            
            with tab1:
                open_demands = [d for d in st.session_state.demands if d['status'] == "Open"]
                if not open_demands:
                    st.write("No active demands right now.")
                for d in open_demands:
                    with st.container(border=True):
                        st.write(f"### {d['crop']} - {d['qty']}")
                        st.write(f"**Offered Price:** ₹{d['price']} | **Consumer:** {d['consumer']}")
                        st.write(f"**Delivery:** {d['delivery']}")
                        if st.button("Accept & Finalize", key=f"acc_{d['id']}"):
                            d['status'] = "Closed"
                            st.session_state.agreements.append({
                                "id": f"AGR-{random.randint(1000,9999)}", "date": str(date.today()),
                                "consumer": d['consumer'], "producer": st.session_state.user,
                                "crop": d['crop'], "qty": d['qty'], "price": d['price']
                            })
                            st.rerun()
                            
            with tab2:
                if not st.session_state.agreements:
                    st.write("No agreements generated yet.")
                for a in st.session_state.agreements:
                    st.success(f"**{a['id']}** | {a['date']} | {a['crop']} ({a['qty']}) at ₹{a['price']}/unit\n\n**Buyer:** {a['consumer']} | **Seller:** {a['producer']}")

    # --- SECTION 3: PREDICTIVE SOWING ---
    elif menu == "🌱 Predictive Sowing":
        st.header("Cumulative Sowing Management")
        st.warning("**Over-Sowing Mitigation Algorithm Active:** If >60% of regional farmers cultivate the identical crop variant, it triggers market saturation alerts.")
        
        crop_data = {
            "Paddy": {"percent": 65, "alt": "Millets or Pulses"},
            "Sugarcane": {"percent": 20, "alt": "Groundnut"},
            "Cotton": {"percent": 10, "alt": "Maize"},
            "Others": {"percent": 5, "alt": "N/A"}
        }
        
        st.subheader("Current Village Cultivation Breakdown")
        for crop, data in crop_data.items():
            pct = data["percent"]
            if pct >= 60:
                st.error(f"**{crop}**: {pct}% (⚠️ High Risk! Suggested Alternative: {data['alt']})")
                st.progress(pct / 100)
            else:
                st.write(f"**{crop}**: {pct}%")
                st.progress(pct / 100)