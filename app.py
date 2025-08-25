# app.py — Food Rescue @ Campus (SDG-2)
# Streamlit MVP: CSV storage, role-based flow, codes, dashboard.
# Tested on: streamlit >= 1.32, pandas >= 2.0, python >= 3.9

from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date, time as dtime
import random
import string
from dateutil import tz

# ---------- App Meta ----------
APP_TITLE = "🍱 Food Rescue"
DATA_FILE = Path("surplus.csv")

STATUS_OPEN = "open"
STATUS_CLAIMED = "claimed"
STATUS_COMPLETED = "completed"
STATUS_EXPIRED = "expired"

# ---------- One-time page config ----------
st.set_page_config(page_title="#Food Rescue ", page_icon="🍱", layout="wide")

# ---------- Visual theme (CSS overrides) ----------
st.markdown("""
<style>
#   /* --- App background --- */
#   .stApp {
#     background: linear-gradient(rgba(10,12,20,.35), rgba(10,12,20,.55)),
#                 url('bg.jpg') no-repeat center center fixed;
#       background-image: src"bg.jpg";
#      background-size: cover;
#    }
#    .block-container { padding-top:2.2rem; max-width: 1200px; }

            /* Container */
    body {
      background: pink;
      background-image: url('bg.jpg');
      background-repeat: no-repeat;
      background-size: cover;
      font-family: Arial, sans-serif;
      color: white;
      margin: 0;
      /* padding: 20px; */
    }
  /* --- HERO --- */
  .hero {
    padding:32px;
    margin-bottom:22px;
    text-align: center;
    color: #fff;
    background: rgba(16,15,15,.35);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 22px;
    backdrop-filter: blur(1px);
    box-shadow: 0 20px 50px rgba(0,70,76,.35);
  }
  .hero h1 {
    margin: 0 0 .25rem 0;
    font-family: "Ubuntu", system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    font-weight: 800;
    font-size: clamp(2.4rem, 5vw, 3.4rem);
    # font-color: rgb(1, 248, 198);
    letter-spacing: 20px;
    # text-transform: uppercase;
  }
  .hero p {
    margin: 0;
    color: #e2e8f0;
    font-style: italic;
    letter-spacing: 2px;
    font-family: "Rubik", sans-serif;
  }

  /* --- card grid (centered) --- */
  .card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 48px;
    margin: 22px auto 34px;
    max-width: 980px;
  }
  @media (max-width: 1024px){ .card-grid { grid-template-columns: repeat(3, 1fr); max-width: 100%; } }
  @media (max-width: 900px) { .card-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 640px) { .card-grid { grid-template-columns: 1fr; } }

  /* --- glass cards to match screenshot --- */
  .card {
    background: rgba(0,0,0,.55);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 24px;
    padding: 22px 22px 24px;
    color: #fff;
    text-align: center;
    backdrop-filter: blur(8px);
    box-shadow: 0 18px 40px rgba(0,0,0,.35);
  }
  .card h3 {
    margin: 0 0 6px 0;
    font-size: 1.2rem;
    font-weight: 800;
  }
  .card p {
    margin: 0 0 12px 0;
    color: #cbd5e1;
    font-size: .98rem;
  }

  /* --- primary button --- */
  .stButton>button[kind="primary"] {
    background: linear-gradient(135deg,#fb7185,#ef4444);
    margin-top:12px;
    border: none; color: white; font-weight: 800;
    border-radius: 14px; padding:.7rem 1.25rem;
    box-shadow: 0 10px 24px rgba(239,68,68,.35);
  }
  .btn-dis{
    display:inline-block; margin-top:12px;
    background: linear-gradient(135deg,#fb7185,#ef4444);
    border:none; color:white; font-weight:800;
    border-radius:14px; padding:.7rem 1.25rem; opacity:.75; cursor:not-allowed;
    box-shadow: 0 10px 24px rgba(239,68,68,.35);
  }

  /* --- dashboard chips (unchanged) --- */
  .chip-metric{
    background:rgba(0,0,0,.55);
    border:1px solid rgba(255,255,255,.08);
    border-radius:14px; padding:12px 14px;
    display:flex;flex-direction:column;gap:6px;height:100%;
    backdrop-filter: blur(6px);
  }
  .chip-label{color:#94a3b8;font-size:.85rem}
  .chip-value{font-size:1.4rem;font-weight:800}

  /* --- tabs + code box --- */
  .stTabs [data-baseweb="tab-list"] { gap: 8px; }
  .stTabs [data-baseweb="tab"] { padding: 10px 14px; border-radius: 12px;
    background:rgba(0,0,0,.5); border:1px solid rgba(255,255,255,.08); }
  .codebox { background:rgba(0,0,0,.55); border:1px dashed #334155; padding:.75rem; border-radius:10px; }

  /* --- footer panel (glass) --- */
  .footer {
    border-top: 2px groove #fb7185;
    color: #e0e0e0;
    padding: 1.5rem 1rem;
    width: 80%;
    margin: 0 auto 18px;
    background: rgba(0,0,0,.55);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 18px;
    backdrop-filter: blur(6px);
    box-shadow: 0 18px 40px rgba(0,0,0,.35);
  }
  .footer-links {
    display: flex; justify-content: space-around; flex-wrap: wrap; gap: 24px;
    margin: 0 auto 1rem; padding: 0 12px; text-align: left; max-width: 1000px;
  }
  .footer-links h4 { margin: 0 0 1rem 0; font-size: 1.1rem; color:#eca4af; }
  .footer-links ul { list-style: none; padding: 0; margin: 0; }
  .footer-links li { margin-bottom: 0.5rem; font-size: 0.95rem; color: #caa8a8; }
  .footer-links li:hover { color: #f0c1d2; }
  .social-media { display:flex; justify-content:center; gap:22px; margin-bottom:8px; }
  .social-media img { width:24px; height:auto; }
</style>
""", unsafe_allow_html=True)


# ---------- Helpers ----------
def _ensure_data_file() -> None:
    if not DATA_FILE.exists():
        cols = [
            "id","created_at_iso","donor_name","donor_phone","food_desc","qty_meals",
            "veg_type","allergens","address","ready_until_iso","ready_until_hhmm",
            "status","claimer_name","claimer_phone","donor_code","volunteer_code",
            "completed_at_iso"
        ]
        pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    _ensure_data_file()
    df = pd.read_csv(DATA_FILE, dtype=str)
    if df.empty:
        return df

    # Parse to LOCAL TIME (naive) so comparisons use the same basis as datetime.now()
    for c in ["created_at_iso","ready_until_iso","completed_at_iso"]:
        if c in df.columns:
            s = pd.to_datetime(df[c], errors="coerce", utc=True)
            s = s.dt.tz_convert(tz.tzlocal()).dt.tz_localize(None)
            df[c] = s

    if "qty_meals" in df.columns:
        df["qty_meals"] = pd.to_numeric(df["qty_meals"], errors="coerce").fillna(0).astype(int)

    now = datetime.now()  # local, naive

    def _expire_row(row):
        ru = row.get("ready_until_iso")
        if pd.isna(ru):
            return row["status"]
        if row["status"] in (STATUS_OPEN, STATUS_CLAIMED) and ru < now:
            return STATUS_EXPIRED
        return row["status"]

    df["status"] = df.apply(_expire_row, axis=1)
    return df

def save_data(df: pd.DataFrame) -> None:
    df2 = df.copy()
    for c in ["created_at_iso","ready_until_iso","completed_at_iso"]:
        if c in df2.columns:
            s = pd.to_datetime(df2[c], errors="coerce", utc=True)
            s = s.dt.tz_convert(tz.tzlocal()).dt.tz_localize(None)
            df2[c] = s
    df2.to_csv(DATA_FILE, index=False)
    load_data.clear()

def gen_code(n:int=4) -> str:
    return "".join(random.choices(string.digits, k=n))

def new_id() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S") + "".join(random.choices(string.digits, k=3))

def local_iso(dt_obj: datetime) -> str:
    # Store as LOCAL TZ AWARE ISO string for audit;
    # we'll parse back to local-naive in load/save.
    return dt_obj.astimezone(tz=tz.tzlocal()).isoformat()

def build_ready_until(today: date, hhmm: dtime) -> datetime:
    # returns timezone-aware datetime (local tz)
    naive = datetime.combine(today, hhmm)
    return naive.replace(tzinfo=tz.tzlocal())

def validate_phone(p: str) -> bool:
    return bool(p and p.strip().isdigit() and 7 <= len(p.strip()) <= 13)

def require_session() -> None:
    ss = st.session_state
    ss.setdefault("role", None)
    ss.setdefault("user_name", "")
    ss.setdefault("user_phone", "")

def _reset_role() -> None:
    for k in ["role","user_name","user_phone"]:
        if k in st.session_state:
            del st.session_state[k]
    st.success("Role cleared.")
    st.session_state["_nav_target"] = "Home"
    st.rerun()

# ---------- Navigation ----------
def nav_header() -> str:
    with st.sidebar:
        st.title("Navigation")

        # Support deep-link: ?go=food | ?go=home | ?go=dashboard
        qp = st.query_params
        if "go" in qp:
            want = qp.get("go", "").strip().lower()
            mapping = {"food":"Food Rescue","home":"Home","dashboard":"Dashboard"}
            if want in mapping:
                st.session_state["nav_page"] = mapping[want]

        # Honor programmatic redirects (set by pages)
        target = st.session_state.get("_nav_target")
        if target:
            st.session_state["nav_page"] = target
            del st.session_state["_nav_target"]

        default_index = 1 if st.session_state.get("role") else 0
        page = st.radio(
            "Go to",
            ["Home", "Food Rescue", "Dashboard"],
            key="nav_page",
            index=["Home","Food Rescue","Dashboard"].index(st.session_state.get("nav_page","Home"))
            if "nav_page" in st.session_state else default_index,
        )
        st.markdown("---")
        st.caption("Demo build • Lightweight pseudo-login")
        return page

# ---------- Pages ----------
def home_page():
    # HERO (big title + quote)
    st.markdown(
        """
        <div class="hero">
          <h1>FEED Forward</h1>
          <p>"We don't just feed mouths! we fuel futures!"</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CENTERED GLASS CARDS (match screenshot)
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        #st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🍽️&nbsp;&nbsp;Food Rescue", unsafe_allow_html=True)
        st.markdown("<p>Donate & claim leftover meals on campus.</p>", unsafe_allow_html=True)
        st.button("Open Food Rescue", key="open_food_rescue_btn_home", on_click=lambda: _goto("Food Rescue"), type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        #st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🛒&nbsp;&nbsp;Smart Ration Planner", unsafe_allow_html=True)
        st.markdown("<p>Plan healthy groceries within a budget. (concept)</p>", unsafe_allow_html=True)
        st.markdown('<span class="btn-dis" aria-disabled="true">Coming Soon</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        #st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🗺️&nbsp;&nbsp;Meal Map", unsafe_allow_html=True)
        st.markdown("<p>Find free/low-cost meals nearby. (concept)</p>", unsafe_allow_html=True)
        st.markdown('<span class="btn-dis" aria-disabled="true">Coming Soon</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # GLASS FOOTER (like screenshot)
    st.markdown(
        """
        <footer class="footer">
          <div class="footer-links">
            <div>
              <h4>Explore</h4>
              <ul>
                <li>Donate</li>
                <li>Explorer</li>
                <li>Food Planner</li>
              </ul>
            </div>
            <div>
              <h4>Company</h4>
              <ul>
                <li>About Us</li>
                <li>How It Works</li>
                <li>Community</li>
              </ul>
            </div>
            <div>
              <h4>Account</h4>
              <ul>
                <li>Login/Register</li>
                <li>Dashboard</li>
                <li>Notifications</li>
              </ul>
            </div>
          </div>

          <div class="social-media" aria-label="Social media">
            <a href="#" aria-label="Instagram"><img src="instagram.png" alt="Instagram" /></a>
            <a href="#" aria-label="Twitter"><img src="x.png" alt="Twitter/X" /></a>
            <a href="#" aria-label="YouTube"><img src="Youtube.png" alt="YouTube" /></a>
          </div>

          <p style="text-align:center;margin:0;">© 2025 FeedForward. All rights reserved.</p>
        </footer>
        """,
        unsafe_allow_html=True
    )

def _goto(name:str):
    st.session_state["_nav_target"] = name
    st.rerun()

def role_page():
    st.subheader("Quick Role (no signup)")
    st.write("Choose your role and enter details for coordination.")
    with st.form("role_form", clear_on_submit=False):
        role = st.radio("I am a …", ["Donor", "Volunteer"], horizontal=True)
        name = st.text_input("Your name / organization")
        phone = st.text_input("Phone (digits only)")
        submitted = st.form_submit_button("Continue")
    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
            return
        if not validate_phone(phone):
            st.error("Please enter a valid phone number (digits only, 7–13).")
            return
        st.session_state.role = role.lower()
        st.session_state.user_name = name.strip()
        st.session_state.user_phone = phone.strip()
        st.success(f"Welcome, {name}! You’re set as {role}.")
        _goto("Food Rescue")

def donor_post_page():
    st.subheader("Post Surplus")
    with st.form("post_form", clear_on_submit=True):
        food_desc = st.text_area("What food is available?", placeholder="e.g., Veg biryani, curd, salad")
        qty = st.number_input("Quantity (meals)", min_value=1, max_value=2000, value=10, step=1)
        veg_type = st.selectbox("Type", ["Veg", "Non-veg", "Mixed"])
        until_time = st.time_input("Available until (today)", value=dtime(21, 0))
        allergens = st.text_input("Allergens / notes (optional)", placeholder="peanuts, gluten, dairy…")
        address = st.text_input("Pickup address / location")
        submitted = st.form_submit_button("Post")

    if submitted:
        if not food_desc.strip() or not address.strip():
            st.error("Please fill food description and address.")
            return

        ready_until = build_ready_until(date.today(), until_time)
        df = load_data()
        post = {
            "id": new_id(),
            "created_at_iso": local_iso(datetime.now()),
            "donor_name": st.session_state.user_name,
            "donor_phone": st.session_state.user_phone,
            "food_desc": food_desc.strip(),
            "qty_meals": int(qty),
            "veg_type": veg_type,
            "allergens": allergens.strip(),
            "address": address.strip(),
            "ready_until_iso": local_iso(ready_until),
            "ready_until_hhmm": until_time.strftime("%H:%M"),
            "status": STATUS_OPEN,
            "claimer_name": "",
            "claimer_phone": "",
            "donor_code": gen_code(),
            "volunteer_code": "",
            "completed_at_iso": pd.NaT
        }
        df = pd.concat([df, pd.DataFrame([post])], ignore_index=True)
        save_data(df)
        st.success("Surplus posted! Share this pickup code with the volunteer at handover:")
        st.markdown(f"<div class='codebox'><code>{post['donor_code']}</code></div>", unsafe_allow_html=True)
        st.info("Use **My Posts** to track or mark completed.")

def _update_status(post_id: str, required_status: str, new_status: str, allow_any_status: bool=False):
    df = load_data()
    mask = df["id"] == post_id
    if not mask.any():
        st.error("Invalid Post ID.")
        return
    row = df.loc[mask].iloc[0]
    if (not allow_any_status) and (row["status"] != required_status):
        st.error(f"Post is '{row['status']}'. Expected '{required_status}'.")
        return
    df.loc[mask, "status"] = new_status
    if new_status == STATUS_EXPIRED:
        df.loc[mask, "ready_until_iso"] = datetime.now()

    save_data(df)
    st.success(f"Post {post_id} updated → {new_status}.")

def _complete_post(post_id: str, other_party_code: str, actor="volunteer"):
    df = load_data()
    mask = df["id"] == post_id
    if not mask.any():
        st.error("Invalid Post ID.")
        return
    row = df.loc[mask].iloc[0]
    if row["status"] != STATUS_CLAIMED:
        st.error("Only claimed posts can be completed.")
        return
    expected_code = row["donor_code"] if actor == "volunteer" else row["volunteer_code"]
    if str(other_party_code).strip() != str(expected_code).strip():
        st.error("Code mismatch. Please verify with the other party.")
        return
    df.loc[mask, "status"] = STATUS_COMPLETED
    df.loc[mask, "completed_at_iso"] = local_iso(datetime.now())
    save_data(df)
    st.success("✅ Completed! Meals saved counted on dashboard.")

def donor_my_posts_page():
    st.subheader("My Posts")
    df = load_data()
    mine = df[(df["donor_name"] == st.session_state.user_name) & (df["donor_phone"] == st.session_state.user_phone)]
    if mine.empty:
        st.info("No posts yet.")
        return

    def status_badge(s: str) -> str:
        s = (s or "").lower()
        return {
            "open": "🟢 Open",
            "claimed": "🔵 Claimed",
            "completed": "✅ Completed",
            "expired": "🔴 Expired",
        }.get(s, s)

    mine2 = mine.copy()
    mine2["Status"] = mine2["status"].map(status_badge)
    mine2 = mine2.rename(columns={
        "id":"Post ID","food_desc":"Food","qty_meals":"Meals","veg_type":"Type",
        "ready_until_hhmm":"Until","claimer_name":"Claimer","claimer_phone":"Claimer phone",
        "donor_code":"Pickup code"
    })[["Post ID","Food","Meals","Type","Until","Status","Claimer","Claimer phone","Pickup code"]]

    st.data_editor(
        mine2,
        hide_index=True,
        use_container_width=True,
        disabled=True,
        column_config={
            "Meals": st.column_config.NumberColumn(format="%d", width="small"),
            "Type": st.column_config.TextColumn(width="small"),
            "Until": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="small"),
            "Pickup code": st.column_config.TextColumn(width="small"),
        },
        key="de_myposts",
    )

    st.markdown("### Update a post")
    with st.form("donor_update_any"):
        colA, colB, colC = st.columns([2,2,2])
        with colA:
            target_id = st.text_input("Post ID")
        with colB:
            action = st.selectbox("Action", ["Cancel (expire it)","Mark Completed"])
        with colC:
            vcode = st.text_input("Volunteer code (required for complete)", placeholder="e.g., 4931")
        submitted = st.form_submit_button("Apply")
    if submitted:
        if not target_id.strip():
            st.error("Please enter a Post ID.")
        else:
            if action.startswith("Cancel"):
                _update_status(target_id, STATUS_OPEN, STATUS_EXPIRED, allow_any_status=False)
            else:
                if not vcode.strip():
                    st.error("Volunteer code required to complete.")
                else:
                    _complete_post(target_id, vcode, actor="donor")

def volunteer_find_claim_page():
    st.subheader("Find & Claim")
    df = load_data()
    open_df = df[df["status"] == STATUS_OPEN].copy()
    if open_df.empty:
        st.info("No open posts right now. Check again soon.")
        return

    with st.container():
        f1, f2, f3 = st.columns([1.1,1,1])
        with f1:
            veg_filter = st.radio("Type", ["All","Veg","Non-veg","Mixed"], horizontal=True, key="v_type")
        with f2:
            only_open_now = st.toggle("Only within time window", value=True, key="v_open_now")
        with f3:
            min_meals = st.number_input("Min meals", min_value=0, value=0, step=1, key="v_min_meals")

    now = datetime.now()

    if veg_filter != "All":
        open_df = open_df[open_df["veg_type"] == veg_filter]
    if only_open_now:
        open_df = open_df[pd.to_datetime(open_df["ready_until_iso"], errors="coerce") > now]
    if min_meals > 0:
        open_df = open_df[pd.to_numeric(open_df["qty_meals"], errors="coerce").fillna(0).astype(int) >= min_meals]

    def veg_tag(v: str) -> str:
        return {"Veg":"🥦 Veg","Non-veg":"🍗 Non-veg","Mixed":"🍛 Mixed"}.get(v, v)

    df_display = open_df.copy()
    df_display["Type"] = df_display["veg_type"].map(veg_tag)
    df_display["Until"] = df_display["ready_until_hhmm"]
    df_display = df_display.rename(columns={
        "id":"Post ID","donor_name":"Donor","food_desc":"Food","qty_meals":"Meals",
        "address":"Address","donor_phone":"Phone"
    })[["Post ID","Donor","Food","Meals","Type","Address","Until","Phone"]]

    st.data_editor(
        df_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Meals": st.column_config.NumberColumn(format="%d", step=1, width="small"),
            "Type": st.column_config.TextColumn(width="small"),
            "Until": st.column_config.TextColumn(width="small"),
            "Phone": st.column_config.TextColumn(width="medium"),
            "Food": st.column_config.TextColumn(width="large"),
        },
        disabled=True,
        key="de_openposts",
    )

    st.markdown("### Claim a post")
    with st.form("claim_form"):
        target_id = st.text_input("Enter Post ID to claim")
        submitted = st.form_submit_button("Claim")
    if submitted:
        if not target_id.strip():
            st.error("Please enter a Post ID.")
            return
        df2 = load_data()
        mask = df2["id"] == target_id
        if not mask.any():
            st.error("Invalid Post ID.")
            return
        row = df2.loc[mask].iloc[0]
        if row["status"] != STATUS_OPEN:
            st.error(f"Post is '{row['status']}'. Choose another.")
            return
        vcode = gen_code()
        df2.loc[mask, "status"] = STATUS_CLAIMED
        df2.loc[mask, "claimer_name"] = st.session_state.user_name
        df2.loc[mask, "claimer_phone"] = st.session_state.user_phone
        df2.loc[mask, "volunteer_code"] = vcode
        save_data(df2)
        st.success("Claimed successfully! Share this code with the donor at pickup:")
        st.markdown(f"<div class='codebox'><code>{vcode}</code></div>", unsafe_allow_html=True)
        st.info("Use **My Claims** to finish pickup with the donor’s code.")

def volunteer_my_claims_page():
    st.subheader("My Claims")
    df = load_data()
    mine = df[(df["claimer_name"] == st.session_state.user_name) & (df["claimer_phone"] == st.session_state.user_phone)]
    if mine.empty:
        st.info("You have no claims yet.")
        return

    mine2 = mine.copy()
    mine2["Status"] = mine2["status"].map({
        "open":"🟢 Open","claimed":"🔵 Claimed","completed":"✅ Completed","expired":"🔴 Expired"
    })
    mine2 = mine2.rename(columns={
        "id":"Post ID","donor_name":"Donor","food_desc":"Food","qty_meals":"Meals",
        "veg_type":"Type","address":"Address","ready_until_hhmm":"Until",
        "donor_phone":"Phone","volunteer_code":"Your code"
    })[["Post ID","Donor","Food","Meals","Type","Address","Until","Status","Phone","Your code"]]

    st.data_editor(
        mine2,
        hide_index=True,
        use_container_width=True,
        disabled=True,
        column_config={
            "Meals": st.column_config.NumberColumn(format="%d", width="small"),
            "Type": st.column_config.TextColumn(width="small"),
            "Until": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="small"),
        },
        key="de_myclaims",
    )

    st.markdown("### Complete a pickup")
    with st.form("vol_complete"):
        c1, c2 = st.columns(2)
        with c1:
            target_id = st.text_input("Post ID")
        with c2:
            dcode = st.text_input("Donor's pickup code")
        finish = st.form_submit_button("Mark Completed")
    if finish:
        if not target_id.strip() or not dcode.strip():
            st.error("Enter both Post ID and donor code.")
        else:
            _complete_post(target_id, dcode, actor="volunteer")

def dashboard_page():
    st.header("📊 Impact Dashboard")
    df = load_data()
    total_posts = int(len(df))
    saved_meals = int(df[df["status"] == STATUS_COMPLETED]["qty_meals"].sum()) if not df.empty else 0
    open_posts = int((df["status"] == STATUS_OPEN).sum()) if not df.empty else 0
    claimed_posts = int((df["status"] == STATUS_CLAIMED).sum()) if not df.empty else 0
    expired_posts = int((df["status"] == STATUS_EXPIRED).sum()) if not df.empty else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    for col, label, value in [
        (col1, "Total posts", total_posts),
        (col2, "Meals saved", saved_meals),
        (col3, "Open", open_posts),
        (col4, "Claimed", claimed_posts),
        (col5, "Expired", expired_posts),
    ]:
        with col:
            st.markdown(
                f"""
                <div class="chip-metric">
                  <div class="chip-label">{label}</div>
                  <div class="chip-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if not df.empty:
        by_status = (
            df.groupby("status")["qty_meals"].sum()
            .reindex([STATUS_OPEN, STATUS_CLAIMED, STATUS_COMPLETED, STATUS_EXPIRED])
            .fillna(0).astype(int)
        )
        st.markdown("#### Meals by status")
        st.bar_chart(by_status)

        st.markdown("#### Top contributors")
        donors = (
            df.groupby("donor_name")["qty_meals"].sum().sort_values(ascending=False).head(5)
        )
        volunteers = (
            df[df["status"] == STATUS_COMPLETED]
            .groupby("claimer_name")["qty_meals"].sum().sort_values(ascending=False).head(5)
        )
        colA, colB = st.columns(2)
        with colA:
            st.write("**Donors**")
            if donors.empty:
                st.caption("No donors yet.")
            else:
                st.table(donors.rename("meals").astype(int))
        with colB:
            st.write("**Volunteers**")
            if volunteers.empty:
                st.info("No completed rescues yet.")
            else:
                st.table(volunteers.rename("meals").astype(int))

        st.download_button(
            "Download data (CSV)",
            data=DATA_FILE.read_bytes(),
            file_name="surplus.csv",
            mime="text/csv",
            type="primary",
        )
    else:
        st.info("No data yet. Post and claim to see impact.")

def food_rescue_router():
    require_session()
    if not st.session_state.role:
        role_page()
        return

    st.info(
        f"You are logged in as **{st.session_state.role.capitalize()}** – "
        f"{st.session_state.user_name} ({st.session_state.user_phone})"
    )

    if st.session_state.role == "donor":
        tabs = st.tabs(["Post Surplus", "My Posts"])
        with tabs[0]:
            donor_post_page()
        with tabs[1]:
            donor_my_posts_page()
    else:
        tabs = st.tabs(["Find & Claim", "My Claims"])
        with tabs[0]:
            volunteer_find_claim_page()
        with tabs[1]:
            volunteer_my_claims_page()

    st.button("Switch Role", on_click=_reset_role)

# ---------- Main router ----------
def main():
    page = nav_header()
    st.title(APP_TITLE)

    if page == "Home":
        home_page()
    elif page == "Food Rescue":
        food_rescue_router()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()