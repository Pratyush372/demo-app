# app.py — Food Rescue @ Campus (SDG-2)
# Streamlit MVP: CSV storage, role-based flow, codes, dashboard.
# Tested on Streamlit >= 1.32

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date, time as dtime, timezone
import random
import string
from dateutil import tz

# ---------- Config ----------
APP_TITLE = "🍱 Food Rescue @ Campus"
DATA_FILE = Path("surplus.csv")

STATUS_OPEN = "open"
STATUS_CLAIMED = "claimed"
STATUS_COMPLETED = "completed"
STATUS_EXPIRED = "expired"

# ---------- Helpers ----------
def _ensure_data_file():
    if not DATA_FILE.exists():
        cols = [
            "id","created_at_iso","donor_name","donor_phone","food_desc","qty_meals",
            "veg_type","allergens","address","ready_until_iso","ready_until_hhmm",
            "status","claimer_name","claimer_phone","donor_code","volunteer_code",
            "completed_at_iso"
        ]
        pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

@st.cache_data(show_spinner=False)
def load_data():
    _ensure_data_file()
    df = pd.read_csv(DATA_FILE)
    # Normalize types
    for c in ["created_at_iso","ready_until_iso","completed_at_iso"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    # Auto expire
    now = datetime.now(tz=tz.tzlocal())
    def _expire(row):
        if pd.isna(row["ready_until_iso"]):
            return row["status"]
        if row["status"] in [STATUS_OPEN, STATUS_CLAIMED] and row["ready_until_iso"] < now:
            return STATUS_EXPIRED
        return row["status"]
    if not df.empty:
        df["status"] = df.apply(_expire, axis=1)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    load_data.clear()  # refresh cache

def gen_code(n=4):
    return "".join(random.choices(string.digits, k=n))

def new_id():
    # short unique id (timestamp + random)
    return datetime.now().strftime("%Y%m%d%H%M%S") + "".join(random.choices(string.digits, k=3))

def local_iso(dt_obj: datetime) -> str:
    return dt_obj.astimezone(tz=tz.tzlocal()).isoformat()

def build_ready_until(today: date, hhmm: dtime) -> datetime:
    # today + time in local tz
    local = datetime.combine(today, hhmm)
    return local.replace(tzinfo=tz.tzlocal())

def validate_phone(p: str) -> bool:
    return p and p.strip().isdigit() and 7 <= len(p.strip()) <= 13

def require_session():
    if "role" not in st.session_state:
        st.session_state.role = None
        st.session_state.user_name = ""
        st.session_state.user_phone = ""

# ---------- UI components ----------
def nav_header():
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Go to",
            ["Home", "Food Rescue", "Dashboard"],
            index=1 if st.session_state.get("role") else 0,
        )
        st.markdown("---")
        st.caption("Simple demo • no real authentication")
        return page

def home_page():
    st.title("SDG-2: Zero Hunger – Our Solutions")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.header("🍱 Food Rescue")
        st.write("Donate & claim leftover meals on campus.")
        if st.button("Open Food Rescue", key="open_food_rescue"):
            st.session_state._nav_target = "Food Rescue"

    with c2:
        st.header("🛒 Smart Ration Planner")
        st.write("Plan healthy groceries within a budget. (concept)")
        st.button("Coming soon", disabled=True, key="soon_ration")

    with c3:
        st.header("🗺️ Meal Map")
        st.write("Find free/low-cost meals nearby. (concept)")
        st.button("Coming soon", disabled=True, key="soon_meal")


def role_page():
    st.subheader("Quick Role (no signup)")
    st.write("Choose your role and enter basic details for contact.")
    with st.form("role_form", clear_on_submit=False):
        role = st.radio("I am a …", ["Donor", "Volunteer"], horizontal=True)
        name = st.text_input("Your name / organization")
        phone = st.text_input("Phone (for coordination)")
        submitted = st.form_submit_button("Continue")
    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
            return
        if not validate_phone(phone):
            st.error("Please enter a valid phone number (digits only).")
            return
        st.session_state.role = role.lower()
        st.session_state.user_name = name.strip()
        st.session_state.user_phone = phone.strip()
        st.success(f"Welcome, {name}! You’re set as {role}.")
        st.rerun()

def donor_post_page():
    st.subheader("Post Surplus")
    with st.form("post_form", clear_on_submit=True):
        food_desc = st.text_area("What food is available?", placeholder="e.g., Veg biryani, curd, salad")
        qty = st.number_input("Quantity (meals)", min_value=1, max_value=2000, value=10, step=1)
        veg_type = st.selectbox("Type", ["Veg", "Non-veg", "Mixed"])
        allergens = st.text_input("Allergens / notes (optional)", placeholder="peanuts, gluten, dairy, etc.")
        address = st.text_input("Pickup address / location")
        today = date.today()
        until_time = st.time_input("Available until (today)", value=dtime(21, 0))
        submitted = st.form_submit_button("Post")
    if submitted:
        if not food_desc.strip() or not address.strip():
            st.error("Please fill food description and address.")
            return
        ready_until = build_ready_until(today, until_time)
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
        st.code(post["donor_code"])
        st.info("Use 'My Posts' to track or mark completed.")

def donor_my_posts_page():
    st.subheader("My Posts")
    df = load_data()
    mine = df[(df["donor_name"] == st.session_state.user_name) & (df["donor_phone"] == st.session_state.user_phone)]
    if mine.empty:
        st.info("No posts yet.")
        return
    mine_display = mine[[
        "id","food_desc","qty_meals","veg_type","ready_until_hhmm","status",
        "claimer_name","claimer_phone","donor_code"
    ]].sort_values(by="id", ascending=False)
    st.dataframe(mine_display, use_container_width=True, hide_index=True)
    st.caption("Tip: Share the pickup code with the volunteer to complete the handover.")

    with st.expander("Update a post"):
        target_id = st.text_input("Enter Post ID to update")
        colA, colB = st.columns(2)
        with colA:
            if st.button("Cancel Post"):
                _update_status(target_id, STATUS_OPEN, STATUS_EXPIRED, allow_any_status=False)
        with colB:
            if st.button("Mark Completed (requires volunteer code)"):
                df2 = load_data()
                row = df2[df2["id"] == target_id]
                if row.empty:
                    st.error("Invalid Post ID.")
                else:
                    if row.iloc[0]["status"] != STATUS_CLAIMED:
                        st.error("Post must be in 'claimed' status.")
                    else:
                        vcode = st.text_input("Enter volunteer code", key="vcode_donor")
                        if vcode and st.button("Confirm Complete", key="confirm_complete_donor"):
                            _complete_post(target_id, vcode, actor="donor")

def _update_status(post_id, required_status, new_status, allow_any_status=False):
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
        df.loc[mask, "ready_until_iso"] = datetime.now(tz=tz.tzlocal())
    save_data(df)
    st.success(f"Post {post_id} updated → {new_status}.")

def _complete_post(post_id, other_party_code, actor="volunteer"):
    # actor = who initiates completion. We verify the opposite code.
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

def volunteer_find_claim_page():
    st.subheader("Find & Claim")
    df = load_data()
    open_df = df[df["status"] == STATUS_OPEN].copy()
    if open_df.empty:
        st.info("No open posts right now. Check again soon.")
        return

    # Simple filters
    col1, col2 = st.columns(2)
    with col1:
        veg_filter = st.selectbox("Filter by type", ["All","Veg","Non-veg","Mixed"])
    with col2:
        only_open_now = st.checkbox("Only those still within time window", value=True)

    now = datetime.now(tz=tz.tzlocal())
    if veg_filter != "All":
        open_df = open_df[open_df["veg_type"] == veg_filter]
    if only_open_now:
        open_df = open_df[pd.to_datetime(open_df["ready_until_iso"], errors="coerce") > now]

    # Display
    show_cols = ["id","donor_name","food_desc","qty_meals","veg_type","address","ready_until_hhmm","donor_phone"]
    st.dataframe(open_df[show_cols].sort_values("id", ascending=False), use_container_width=True, hide_index=True)

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
        st.code(vcode)
        st.info("Use 'My Claims' to finish pickup with the donor’s code.")

def volunteer_my_claims_page():
    st.subheader("My Claims")
    df = load_data()
    mine = df[(df["claimer_name"] == st.session_state.user_name) & (df["claimer_phone"] == st.session_state.user_phone)]
    if mine.empty:
        st.info("You have no claims yet.")
        return
    st.dataframe(
        mine[["id","donor_name","food_desc","qty_meals","veg_type","address","ready_until_hhmm","status","donor_phone","volunteer_code"]],
        use_container_width=True, hide_index=True
    )

    with st.expander("Complete a pickup"):
        target_id = st.text_input("Enter Post ID")
        dcode = st.text_input("Enter donor's pickup code (given by donor)")
        if st.button("Mark Completed"):
            if not target_id.strip() or not dcode.strip():
                st.error("Enter both Post ID and donor code.")
            else:
                _complete_post(target_id, dcode, actor="volunteer")

def dashboard_page():
    st.header("📊 Impact Dashboard")
    df = load_data()
    total_posts = len(df)
    saved_meals = int(df[df["status"].isin([STATUS_COMPLETED])]["qty_meals"].sum())
    open_posts = int((df["status"] == STATUS_OPEN).sum())
    claimed_posts = int((df["status"] == STATUS_CLAIMED).sum())
    expired_posts = int((df["status"] == STATUS_EXPIRED).sum())

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total posts", total_posts)
    col2.metric("Meals saved", saved_meals)
    col3.metric("Open", open_posts)
    col4.metric("Claimed", claimed_posts)
    col5.metric("Expired", expired_posts)

    if not df.empty:
        by_status = df.groupby("status")["qty_meals"].sum().reindex(
            [STATUS_OPEN, STATUS_CLAIMED, STATUS_COMPLETED, STATUS_EXPIRED]
        ).fillna(0)
        st.bar_chart(by_status)

        st.markdown("#### Top donors / volunteers")
        donors = (df.groupby("donor_name")["qty_meals"].sum().sort_values(ascending=False).head(5))
        volunteers = (df[df["status"]==STATUS_COMPLETED].groupby("claimer_name")["qty_meals"].sum().sort_values(ascending=False).head(5))
        colA, colB = st.columns(2)
        with colA:
            st.write("**Donors**")
            st.table(donors.rename("meals").astype(int))
        with colB:
            st.write("**Volunteers**")
            if volunteers.empty:
                st.info("No completed rescues yet.")
            else:
                st.table(volunteers.rename("meals").astype(int))

        st.download_button("Download data (CSV)", data=DATA_FILE.read_bytes(), file_name="surplus.csv", mime="text/csv")
    else:
        st.info("No data yet. Post and claim to see impact.")

def food_rescue_simple_page():
    st.subheader("Food Rescue – Quick Actions")
    tab_donor, tab_receiver = st.tabs(["🍱 Donor Box", "🤝 Receiver Box"])

    # ---------- DONOR BOX ----------
    with tab_donor:
        st.markdown("Post surplus food so receivers can claim it.")
        with st.form("donor_box_form", clear_on_submit=True):
            veg_type = st.selectbox("What type of food?", ["Veg","Non-veg","Mixed"])
            food_desc = st.text_area("Food details", placeholder="e.g., Veg biryani + curd, 10 plates")
            qty = st.number_input("Quantity (meals)", min_value=1, max_value=2000, value=10, step=1)
            address = st.text_input("Pickup location/address")
            donor_name = st.text_input("Your name / canteen")
            donor_phone = st.text_input("Contact phone (digits only)")
            until_time = st.time_input("Available until (today)", value=dtime(21, 0))
            notes = st.text_input("Other details (optional)")
            submit_post = st.form_submit_button("Post surplus")

        if submit_post:
            if not (food_desc.strip() and address.strip() and donor_name.strip() and donor_phone.strip()):
                st.error("Please fill food details, address, name and phone.")
            elif not validate_phone(donor_phone):
                st.error("Phone must be digits, 7–13 characters.")
            else:
                ready_until = build_ready_until(date.today(), until_time)
                df = load_data()
                post = {
                    "id": new_id(),
                    "created_at_iso": local_iso(datetime.now()),
                    "donor_name": donor_name.strip(),
                    "donor_phone": donor_phone.strip(),
                    "food_desc": food_desc.strip(),
                    "qty_meals": int(qty),
                    "veg_type": veg_type,
                    "allergens": notes.strip(),
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
                st.success("Posted! Share this code with the receiver during pickup:")
                st.code(post["donor_code"])

        st.markdown("**Recent posts by you (filter by phone):**")
        phone_filter = st.text_input("Your phone", key="donor_phone_filter")
        dfv = load_data()
        if phone_filter.strip():
            dfv = dfv[dfv["donor_phone"] == phone_filter.strip()]
        cols = ["id","food_desc","qty_meals","veg_type","ready_until_hhmm","status","claimer_name","donor_code"]
        if not dfv.empty:
            st.dataframe(dfv[cols].sort_values("id", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.caption("No matching posts yet.")

    # ---------- RECEIVER BOX ----------
    with tab_receiver:
        st.markdown("Find open posts and claim them.")
        df = load_data()
        open_df = df[df["status"] == STATUS_OPEN].copy()

        colf1, colf2 = st.columns(2)
        with colf1:
            veg_filter = st.selectbox("Filter by type", ["All","Veg","Non-veg","Mixed"], key="rx_veg")
        with colf2:
            only_open_now = st.checkbox("Only still within time window", value=True, key="rx_open_now")

        now = datetime.now(tz=tz.tzlocal())
        if veg_filter != "All":
            open_df = open_df[open_df["veg_type"] == veg_filter]
        if only_open_now:
            open_df = open_df[pd.to_datetime(open_df["ready_until_iso"], errors="coerce") > now]

        show_cols = ["id","donor_name","food_desc","qty_meals","veg_type","address","ready_until_hhmm","donor_phone"]
        if not open_df.empty:
            st.dataframe(open_df[show_cols].sort_values("id", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No open posts right now.")

        st.markdown("### Claim a post")
        with st.form("receiver_claim_form"):
            post_id = st.text_input("Post ID to claim")
            your_name = st.text_input("Your name / organization")
            your_phone = st.text_input("Your phone (digits only)")
            do_claim = st.form_submit_button("Claim")
        if do_claim:
            df2 = load_data()
            if not (post_id.strip() and your_name.strip() and your_phone.strip()):
                st.error("Enter Post ID, your name and phone.")
            elif not validate_phone(your_phone):
                st.error("Phone must be digits, 7–13 characters.")
            elif not (df2["id"] == post_id).any():
                st.error("Invalid Post ID.")
            else:
                row = df2[df2["id"] == post_id].iloc[0]
                if row["status"] != STATUS_OPEN:
                    st.error(f"Post is '{row['status']}'. Choose another.")
                else:
                    vcode = gen_code()
                    df2.loc[df2["id"] == post_id, ["status","claimer_name","claimer_phone","volunteer_code"]] = \
                        [STATUS_CLAIMED, your_name.strip(), your_phone.strip(), vcode]
                    save_data(df2)
                    st.success("Claimed! Show this code to the donor at pickup:")
                    st.code(vcode)

        st.markdown("### Complete pickup")
        with st.form("receiver_complete_form"):
            c_post_id = st.text_input("Post ID", key="rx_complete_pid")
            donor_code = st.text_input("Donor's pickup code", key="rx_complete_code")
            do_complete = st.form_submit_button("Mark Completed")
        if do_complete:
            if not c_post_id.strip() or not donor_code.strip():
                st.error("Enter both Post ID and donor code.")
            else:
                _complete_post(c_post_id, donor_code, actor="volunteer")

# ---------- Main ----------
def food_rescue_router():
    require_session()
    if not st.session_state.role:
        role_page()
        return

    st.info(f"You are logged in as **{st.session_state.role.capitalize()}** – {st.session_state.user_name} ({st.session_state.user_phone})")
    tab_names = []
    if st.session_state.role == "donor":
        tab_names = ["Post Surplus", "My Posts"]
    else:
        tab_names = ["Find & Claim", "My Claims"]

    tabs = st.tabs(tab_names)
    if st.session_state.role == "donor":
        with tabs[0]:
            donor_post_page()
        with tabs[1]:
            donor_my_posts_page()
    else:
        with tabs[0]:
            volunteer_find_claim_page()
        with tabs[1]:
            volunteer_my_claims_page()

    st.button("Switch Role", on_click=_reset_role)

def _reset_role():
    for k in ["role","user_name","user_phone"]:
        if k in st.session_state:
            del st.session_state[k]
    st.success("Role cleared.")
    st.rerun()

def main():
    st.set_page_config(page_title="Food Rescue @ Campus", page_icon="🍱", layout="wide")
    page = nav_header()
    target = st.session_state.pop("_nav_target", None)
    if target:
        page = target
    st.title(APP_TITLE)

    if page == "Home":
        home_page()
    elif page == "Food Rescue":
        food_rescue_router()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
