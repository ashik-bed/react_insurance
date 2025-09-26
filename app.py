# ---------------------------
# IMPORTS
# ---------------------------
import streamlit as st
import json
import os
from datetime import datetime
import bcrypt
import matplotlib.pyplot as plt

# ---------------------------
# CONFIG (must be FIRST Streamlit call, only once)
# ---------------------------
st.set_page_config(
    page_title="CRM System",   # use global system title
    page_icon="💼",            # main system icon
    layout="wide",
    initial_sidebar_state="expanded"
)


# CONFIG
# ---------------------------
DATA_FILE = "crm_data.json"
UPLOAD_DIR = "uploads"


# ---------------------------
# HELPERS
# ---------------------------
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Error loading data file. Starting with fresh data.")
            return {
                "users": {},
                "customers": {},
                "dashboard": {"text": "Welcome to CRM System. Please login to continue.", "image_path": None},
            }
    return {
        "users": {},
        "customers": {},
        "dashboard": {"text": "Welcome to CRM System. Please login to continue.", "image_path": None},
    }


def save_data(data):
    try:
        # json.dump signature expects (obj, file, ...). Fixed from your original.
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        # Clear the cache so load_data returns fresh content next time
        try:
            st.cache_data.clear()
        except Exception:
            # If Streamlit version doesn't support this API, ignore silently
            pass
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def check_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False


def generate_customer_id():
    return f"CUST-{int(datetime.now().timestamp())}"


# ---------------------------
# STATUS LABELS (Updated with lighter colors)
# ---------------------------
status_labels = {
    "submitted": ("🔴 Submitted", "#ff6b6b"),
    "approved_by_area_manager": ("🟡 Area Manager Approved", "#ffd93d"),
    "approved_by_agm": ("🟢 AGM Approved", "#6bcf7f"),
}

# ---------------------------
# INITIAL DATA & FOLDERS
# ---------------------------
db = load_data()
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Default admin - ensure it's created if missing
if "ASHIK" not in db["users"]:
    hashed_pw = hash_password("ASHph7#")
    db["users"]["ASHIK"] = {
        "username": "ASHIK",
        "password": hashed_pw,
        "role": "admin",
        "assigned_branches": [],
        "created_by": "system",
        "created_at": str(datetime.now()),
    }
    save_data(db)

# ---------------------------
# SESSION STATE
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------------------
# CUSTOM CSS FOR PROFESSIONAL UI (Lighter Colors: Blues and Grays)
# ---------------------------
def apply_custom_css():
    st.markdown("""
    <style>
    /* Global Fonts and Colors - Professional Light Theme */
    html, body, [class*="css"] { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    .stApp { 
        background-color: #f8fafc; 
    }

    /* Sidebar Styling - Light Blue Gradient */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #e2e8f0 0%, #cbd5e1 100%); 
        color: #334155; 
        padding: 1rem;
    }
    section[data-testid="stSidebar"] .css-1d391kg, 
    section[data-testid="stSidebar"] .css-qrbaxs { 
        color: #334155 !important; 
    }
    section[data-testid="stSidebar"] h1 {
        color: #1e293b;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Button Styling - Professional Blue */
    div.stButton > button { 
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
        color: white; 
        border-radius: 8px; 
        border: none; 
        padding: 0.75em 1.5em; 
        font-weight: 600; 
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover { 
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%); 
        color: white; 
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    div.stButton > button:active {
        transform: translateY(0);
    }

    /* Input and Select Styling */
    input, textarea, select { 
        border-radius: 8px !important; 
        border: 2px solid #e2e8f0 !important; 
        padding: 0.75em !important; 
        font-size: 14px;
        transition: border-color 0.3s ease;
        background-color: #ffffff;
    }
    input:focus, textarea:focus, select:focus {
        border-color: #3b82f6 !important;
        outline: none;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* Expander Styling */
    .streamlit-expanderHeader { 
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important; 
        font-weight: 600; 
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.75em;
    }

    /* Headers - Dark Blue/Gray */
    h1, h2, h3 { 
        color: #1e293b; 
        font-weight: 700;
    }
    h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
    h2 { font-size: 2rem; margin-bottom: 0.5rem; }
    h3 { font-size: 1.5rem; margin-bottom: 0.5rem; }

    /* Success/Error/Warning Messages - Lighter */
    .stSuccess { background-color: #ecfdf5; border: 1px solid #bbf7d0; color: #166534; }
    .stError { background-color: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
    .stWarning { background-color: #fefce8; border: 1px solid #fef08a; color: #a16207; }

    /* Metrics and Info */
    .stMetric { font-size: 1.2rem; }

    /* Container Padding */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)


apply_custom_css()


#/--------Login-------/

def login_page():
    db_local = load_data()  # Fresh load

    dashboard_text = db_local["dashboard"].get(
        "text", "Welcome to CRM System. Please login to continue."
    )
    dashboard_img = db_local["dashboard"].get("image_path", "")

    # Custom styles
    st.markdown(
        """
        <style>
        .login-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            color: #1e293b;
        }
        .dashboard-text {
            color: #475569;
            font-size: 15px;
            margin: 1rem 0;
        }
        /* Add spacing at top */
        .top-space {
            margin-top: 50px;
        }
        /* Divider line */
        .divider {
            border-left: 2px solid #e2e8f0;
            height: 100%;
            margin: 0 1rem;
        }
        /* Reduce input width for login page */
        .login-input input {
            width: 250px !important;  /* Adjust as needed */
            max-width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Add top space
    st.markdown('<div class="top-space"></div>', unsafe_allow_html=True)

    col1, col_div, col2 = st.columns([1, 0.02, 3], gap="large")  # thinner divider

    # LEFT: LOGIN
    with col1:
        st.markdown('<div class="login-header">🔐 Sign In</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-input">', unsafe_allow_html=True)
        username = st.text_input("👤 Username", placeholder="Enter username", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="login_password")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Sign In", key="login_btn"):
            db_now = load_data()
            if username in db_now["users"]:
                user_data = db_now["users"][username]
                if check_password(password, user_data["password"]):
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.toast(f"✅ Welcome, {username}!", icon="🎉")
                    st.experimental_rerun()
                else:
                    st.error("❌ Invalid password.")
            else:
                st.error("❌ Username not found.")

    # DIVIDER
    with col_div:
        st.markdown('<div class="divider" style="height: 400px;"></div>', unsafe_allow_html=True)

    # RIGHT: DASHBOARD
    with col2:
        st.subheader("CRM System")
        if dashboard_img and os.path.exists(dashboard_img):
            st.image(dashboard_img, use_column_width=True)
        st.markdown(f'<div class="dashboard-text">{dashboard_text}</div>', unsafe_allow_html=True)
        st.caption("Secure customer relationship management platform")


# ---------------------------
# REPORTS PAGE (Updated Icons and Layout)
# ---------------------------
def reports_page(db):
    """
    Display charts & stats. This function uses st.session_state.user if needed for role-based behavior.
    """
    st.header("📊 Reports & Analytics")
    customers = list(db["customers"].values())
    users = list(db["users"].values())
    user = st.session_state.user  # Use current logged-in user

    # Container for reports
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("🏢 Branch-wise Customer Distribution")
        branch_counts = {}
        for c in customers:
            branch = c.get("branch", "Unassigned")
            branch_counts[branch] = branch_counts.get(branch, 0) + 1
        if branch_counts:
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(list(branch_counts.keys()), list(branch_counts.values()),
                          edgecolor='white', linewidth=1.5)
            ax.set_title("Branch-wise Customer Count", fontsize=14, fontweight='bold', pad=20)
            ax.set_ylabel("Number of Customers", fontsize=12)
            ax.set_xlabel("Branch", fontsize=12)
            ax.tick_params(axis="x", rotation=45)
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.05,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("📋 No customer data available for branch-wise analysis.")

    with col2:
        st.subheader("📈 Customer Status Distribution")
        status_counts = {}
        for c in customers:
            status = c.get("status", "submitted")
            status_counts[status] = status_counts.get(status, 0) + 1
        if status_counts:
            labels = [status_labels.get(k, (k.title(), "#94a3b8"))[0] for k in status_counts.keys()]
            colors = [status_labels.get(k, (k.title(), "#94a3b8"))[1] for k in status_counts.keys()]
            fig, ax = plt.subplots(figsize=(8, 6))
            wedges, texts, autotexts = ax.pie(
                list(status_counts.values()),
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                explode=(0.05,) * len(status_counts)
            )
            ax.axis("equal")
            ax.set_title("Customer Status Distribution", fontsize=14, fontweight='bold', pad=20)
            plt.setp(autotexts, size=10, weight="bold")
            st.pyplot(fig)
        else:
            st.info("📋 No customer data available for status analysis.")

        # Role-wise user count (moved outside columns for proper layout)
        st.subheader("👥 User Role Distribution")
        role_counts = {}
        for u in users:
            role = u.get("role", "branch")
            role_counts[role] = role_counts.get(role, 0) + 1
        if role_counts:
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(role_counts.keys(), role_counts.values(), edgecolor='white', linewidth=1.5)
            ax.set_title("Role-wise User Count", fontsize=14, fontweight='bold', pad=20)
            ax.set_ylabel("Number of Users", fontsize=12)
            ax.set_xlabel("Role", fontsize=12)
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.05,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("👥 No user data available for role analysis.")


# ---------------------------
# Page functions that were referenced but not defined earlier.
# These reuse logic from your original big block (kept semantics).
# ---------------------------
def create_agm_page(user, db):
    st.header("👥 Create New AGM")
    new_username = st.text_input("AGM Username", placeholder="Enter unique username", key="create_agm_username")
    new_password = st.text_input("AGM Password", type="password",
                                 placeholder="Enter secure password (min 6 chars)", key="create_agm_password")
    if st.button("✅ Create AGM", key="create_agm_btn"):
        if not new_username:
            st.error("❌ Username is required")
        elif new_username in db["users"]:
            st.error("❌ Username already exists")
        elif len(new_password) < 6:
            st.error("❌ Password must be at least 6 characters")
        else:
            db["users"][new_username] = {
                "username": new_username,
                "password": hash_password(new_password),
                "role": "AGM",
                "assigned_branches": [],
                "created_by": user["username"],
                "created_at": str(datetime.now())
            }
            if save_data(db):
                st.success("✅ AGM created successfully!")
                st.experimental_rerun()


def create_area_manager_page(user, db):
    st.header("👥 Create New Area Manager")
    am_username = st.text_input("Area Manager Username", placeholder="Enter unique username", key="am_username")
    am_password = st.text_input("Password", type="password", placeholder="Enter secure password (min 6 chars)",
                                key="am_password")
    am_branches = st.text_input("Assign Branches (comma-separated)", placeholder="e.g., Branch A, Branch B",
                                key="am_branches")
    if st.button("✅ Create Area Manager", key="am_create_btn"):
        if not am_username:
            st.error("❌ Username is required")
        elif am_username in db["users"]:
            st.error("❌ Username already exists")
        elif len(am_password) < 6:
            st.error("❌ Password must be at least 6 characters")
        else:
            branches = [b.strip() for b in am_branches.split(",") if b.strip()]
            db["users"][am_username] = {
                "username": am_username,
                "password": hash_password(am_password),
                "role": "area_manager",
                "assigned_branches": branches,
                "created_by": user["username"],
                "created_at": str(datetime.now())
            }
            if save_data(db):
                st.success("✅ Area Manager created successfully!")
                st.experimental_rerun()


def create_branch_user_page(user, db):
    st.header("👥 Create New Branch User")
    bu_username = st.text_input("Branch User Username", placeholder="Enter unique username", key="bu_username")
    bu_password = st.text_input("Password", type="password", placeholder="Enter secure password (min 6 chars)",
                                key="bu_password")
    if user["role"] == "area_manager":
        bu_branch = st.selectbox("Assign Branch", options=[""] + user.get("assigned_branches", []), key="bu_branch_select")
    else:
        bu_branch = st.text_input("Assign Branch", placeholder="Enter branch name", key="bu_branch_input")
    if st.button("✅ Create Branch User", type="primary", key="bu_create_btn"):
        if not bu_username:
            st.error("❌ Username is required")
        elif bu_username in db["users"]:
            st.error("❌ Username already exists")
        elif len(bu_password) < 6:
            st.error("❌ Password must be at least 6 characters")
        elif not bu_branch:
            st.error("❌ Branch assignment is required")
        else:
            db["users"][bu_username] = {
                "username": bu_username,
                "password": hash_password(bu_password),
                "role": "branch",
                "assigned_branches": [bu_branch.strip()],
                "created_by": user["username"],
                "created_at": str(datetime.now())
            }
            if save_data(db):
                st.success("✅ Branch User created successfully!")
                st.experimental_rerun()


def submit_customer_page(user, db):
    st.header("📝 Submit New Customer")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Customer Name", placeholder="Enter full name", help="Full name of the customer",
                             key="cust_name")
        phone = st.text_input("📞 Phone Number", placeholder="10 digits", max_chars=10,
                              help="Enter 10-digit phone number", key="cust_phone")
    with col2:
        aadhaar = st.text_input("🆔 Aadhaar Number", placeholder="12 digits", max_chars=12,
                                help="Enter 12-digit Aadhaar number", key="cust_aadhaar")
        email = st.text_input("📧 Email (optional)", placeholder="Enter email address", key="cust_email")

    file = st.file_uploader("📎 Upload Supporting Document", type=["pdf", "jpg", "png", "jpeg"],
                            help="Upload customer document (PDF/Image)", key="cust_file")

    if st.button("✅ Submit Customer", type="primary", use_container_width=True, key="submit_customer_btn"):
        branch = user["assigned_branches"][0] if user.get("assigned_branches") else "Unassigned"
        if not name or not phone or not aadhaar or not file:
            st.error("❌ All required fields (Name, Phone, Aadhaar, Document) must be provided")
        elif not phone.isdigit() or len(phone) != 10:
            st.error("❌ Phone number must be exactly 10 digits")
        elif not aadhaar.isdigit() or len(aadhaar) != 12:
            st.error("❌ Aadhaar number must be exactly 12 digits")
        else:
            try:
                cid = generate_customer_id()
                fpath = os.path.join(UPLOAD_DIR, f"{cid}_{file.name}")
                with open(fpath, "wb") as f:
                    f.write(file.getbuffer())
                db["customers"][cid] = {
                    "customer_id": cid,
                    "name": name,
                    "phone": phone,
                    "aadhaar_number": aadhaar,
                    "email": email or "",
                    "branch": branch,
                    "submitted_by": user["username"],
                    "status": "submitted",
                    "document_path": fpath,
                    "created_at": str(datetime.now()),
                    "updated_at": str(datetime.now())
                }
                if save_data(db):
                    st.success(f"✅ Customer {cid} submitted successfully! Status: {status_labels['submitted'][0]}")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Error submitting customer: {str(e)}")


def view_records_page(user, db):
    st.header("📂 Customer Records")
    search = st.text_input("🔍 Search by Name, ID, or Phone", placeholder="Enter search term", key="record_search")

    # Filter customers based on role
    all_customers = list(db["customers"].values())
    customers = all_customers.copy()

    if user["role"] == "branch":
        customers = [c for c in customers if c["submitted_by"] == user["username"]]
    elif user["role"] == "area_manager":
        customers = [c for c in customers if c["branch"] in user.get("assigned_branches", [])]
    # For AGM and admin: show all

    if search:
        customers = [c for c in customers if
                     search.lower() in c["name"].lower() or
                     search.lower() in c["customer_id"].lower() or
                     search.lower() in c.get("phone", "").lower()]

    if not customers:
        st.info("📋 No customer records found matching the criteria.")
        return

    # Display customers in expanders
    for c in customers:
        with st.expander(
                f"🆔 {c['customer_id']} | 👤 {c['name']} | 📞 {c.get('phone', 'N/A')} | 🏢 {c.get('branch', 'Unassigned')}",
                expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**📧 Email:** {c.get('email', 'N/A')}")
                st.write(f"**👤 Submitted By:** {c.get('submitted_by', 'N/A')}")
                st.write(f"**📅 Created:** {c.get('created_at', 'N/A')}")
                st.write(f"**🔄 Updated:** {c.get('updated_at', 'N/A')}")

            with col2:
                status_label, status_color = status_labels.get(c["status"], (c["status"].title(), "#94a3b8"))
                st.markdown(
                    f"**📊 Status:** <span style='color:{status_color}; font-weight:bold;'>{status_label}</span>",
                    unsafe_allow_html=True)

            # Document download
            doc = c.get("document_path")
            if doc and os.path.exists(doc):
                with open(doc, "rb") as fobj:
                    st.download_button(
                        label="📄 Download Document",
                        data=fobj,
                        file_name=os.path.basename(doc),
                        mime="application/octet-stream"
                    )
            else:
                st.warning("⚠️ Document not found or inaccessible.")

            # Approval actions
            if c["status"] == "submitted" and user["role"] == "area_manager" and c["branch"] in user.get(
                    "assigned_branches", []):
                col_approve, col_space = st.columns([1, 3])
                with col_approve:
                    if st.button(f"✅ Approve as Area Manager", key=f"approve_am_{c['customer_id']}"):
                        c["status"] = "approved_by_area_manager"
                        c["updated_at"] = str(datetime.now())
                        db["customers"][c["customer_id"]] = c
                        if save_data(db):
                            st.success(f"✅ {c['customer_id']} approved by Area Manager!")
                            st.experimental_rerun()

            if c["status"] == "approved_by_area_manager" and user["role"] == "AGM":
                col_approve, col_space = st.columns([1, 3])
                with col_approve:
                    if st.button(f"✅ Approve as AGM", key=f"approve_agm_{c['customer_id']}"):
                        c["status"] = "approved_by_agm"
                        c["updated_at"] = str(datetime.now())
                        db["customers"][c["customer_id"]] = c
                        if save_data(db):
                            st.success(f"✅ {c['customer_id']} approved by AGM!")
                            st.experimental_rerun()


            # Admin delete
            if user["role"] == "admin":
                col_delete, col_space = st.columns([1, 3])
                with col_delete:
                    if st.button(f"🗑️ Delete", key=f"delete_{c['customer_id']}"):
                        try:
                            if c.get("document_path") and os.path.exists(c["document_path"]):
                                os.remove(c["document_path"])
                            del db["customers"][c["customer_id"]]
                            if save_data(db):
                                st.warning(f"⚠️ {c['customer_id']} deleted successfully!")
                                st.experimental_rerun()
                        except Exception as e:
                            st.error(f"❌ Error deleting: {str(e)}")


def settings_page(user, db):
    st.header("⚙️ Admin Settings")
    st.subheader("Dashboard Configuration")

    col1, col2 = st.columns(2)
    with col1:
        dashboard_text = st.text_area(
            "Dashboard Welcome Text",
            value=db["dashboard"].get("text", "Welcome to CRM System. Please login to continue."),
            height=100,
            help="Customize the message shown on the login page",
            key="settings_dashboard_text"
        )
    with col2:
        dashboard_img = st.file_uploader("Upload Dashboard Image", type=["png", "jpg", "jpeg"],
                                         key="settings_dashboard_img")
        # Preview current image if exists
        if db["dashboard"].get("image_path") and os.path.exists(db["dashboard"]["image_path"]):
            st.image(db["dashboard"]["image_path"], caption="Current Dashboard Image", use_column_width=True)
            # Add delete button
            if st.button("🗑️ Delete Dashboard Image", key="delete_dashboard_img"):
                try:
                    os.remove(db["dashboard"]["image_path"])
                except Exception as e:
                    st.error(f"❌ Could not delete image: {str(e)}")
                db["dashboard"]["image_path"] = None
                if save_data(db):
                    st.success("✅ Dashboard image deleted successfully!")
                    st.experimental_rerun()

    if st.button("💾 Update Dashboard", type="primary", key="update_dashboard_btn"):
        db["dashboard"]["text"] = dashboard_text
        if dashboard_img:
            img_path = os.path.join(UPLOAD_DIR, f"dashboard_{int(datetime.now().timestamp())}.jpg")
            with open(img_path, "wb") as f:
                f.write(dashboard_img.getbuffer())
            db["dashboard"]["image_path"] = img_path
        if save_data(db):
            st.success("✅ Dashboard settings updated successfully!")
            st.experimental_rerun()

    st.subheader("📈 System Stats")
    total_customers = len(db["customers"])
    total_users = len(db["users"])
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("👥 Total Users", total_users)
    with col_stats2:
        st.metric("📊 Total Customers", total_customers)
    with col_stats3:
        pending = len([c for c in db["customers"].values() if c["status"] == "submitted"])
        st.metric("⏳ Pending Approvals", pending)

# ---------------------------
# MAIN / DASHBOARD ROUTER
# ---------------------------
def dashboard():
    user = st.session_state.user
    db_local = load_data()

    # Sidebar with username and logout icon
    with st.sidebar:
        st.markdown(
            """
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
            <style>
            .sidebar-user {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }
            .sidebar-user h2 {
                margin: 0;
                font-size: 1.2rem;
            }
            .logout-icon button {
                background: none;
                border: none;
                cursor: pointer;
                font-size: 1.5rem;
                color: #1e293b;
                padding: 0;
            }
            .logout-icon button:hover {
                color: #ef4444;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Layout with columns
        cols = st.columns([6, 1])

        # Username
        with cols[0]:
            st.markdown(f"<h2 style='margin:0;'>👤 {user['username']}</h2>", unsafe_allow_html=True)

        # Logout icon as button
        with cols[1]:
            if st.button("➜", key="logout_btn", help="Logout"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.experimental_rerun()

            # Replace button text with Font Awesome icon
            st.markdown(
                """
                <style>
                button#logout_btn {
                    background: none;
                    border: none;
                    cursor: pointer;
                    font-size: 1.5rem;
                    color: #1e293b;
                }
                button#logout_btn:hover {
                    color: #ef4444;
                }
                </style>
                <script>
                const btn = window.parent.document.querySelector('button#logout_btn');
                if(btn){ btn.innerHTML = '<i class="fa-regular fa-right-from-bracket"></i>'; }
                </script>
                """,
                unsafe_allow_html=True
            )

        # Hidden input to detect logout click
        if "logout_flag" not in st.session_state:
            st.session_state.logout_flag = 0
        # Trigger logout
        if st.session_state.logout_flag == 1:
            st.session_state.logged_in = False
            st.session_state.user = None
            st.experimental_rerun()

    # Build menu options depending on role
    if user["role"] == "admin":
        menu = [
            "👥 Create AGM",
            "👥 Create Area Manager",
            "👥 Create Branch User",
            "📂 View Records",
            "⚙️ Settings",
            "📊 Reports"
        ]
    elif user["role"] == "AGM":
        menu = [
            "👥 Create Area Manager",  # AGM can create Area Managers
            "📂 View Records",
            "📊 Reports"
        ]
    elif user["role"] == "area_manager":
        menu = [
            "👥 Create Branch User",  # Area Manager can create Branch Users in their branches
            "📂 View Records",
            "📊 Reports"
        ]
    elif user["role"] == "branch":
        menu = [
            "📝 Submit Customer",
            "📂 View Records",
            "📊 Reports"
        ]
    else:
        menu = ["📂 View Records", "📊 Reports"]

    choice = st.sidebar.radio("📋 Navigation", menu, key="main_menu_radio")

    # Route pages
    if choice == "📊 Reports":
        reports_page(db_local)
    elif choice == "📝 Submit Customer":
        submit_customer_page(user, db_local)
    elif choice == "📂 View Records":
        view_records_page(user, db_local)
    elif choice == "⚙️ Settings" and user["role"] == "admin":
        settings_page(user, db_local)
    elif choice == "👥 Create AGM" and user["role"] == "admin":
        create_agm_page(user, db_local)
    elif choice == "👥 Create Area Manager" and user["role"] in ["admin", "AGM"]:
        create_area_manager_page(user, db_local)
    elif choice == "👥 Create Branch User" and user["role"] in ["admin", "area_manager"]:
        create_branch_user_page(user, db_local)
    else:
        st.info("Select a page from the sidebar.")

# ---------------------------
# MAIN EXECUTION BLOCK (Router for Login/Dashboard)
# ---------------------------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard()


if __name__ == "__main__":
    main()
