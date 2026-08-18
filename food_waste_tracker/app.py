"""
app.py
------
Streamlit GUI for the Food Waste & Surplus Redistribution Tracker.

Run with:
    streamlit run app.py

This is the presentation layer only - all file I/O lives in
file_manager.py and all validation lives in validators.py, keeping the
program modular as required.
"""

import pandas as pd
import streamlit as st

import file_manager as fm
import validators as val
from models import Donor, FoodItem, DonationRecord

st.set_page_config(
    page_title="Food Waste & Surplus Redistribution Tracker",
    page_icon="🍲",
    layout="wide",
)

# ---------------------------------------------------------------- styling --
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1c1f26;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
    div[data-testid="stMetricValue"] { color: #4CAF50; }
    .success-box {
        padding: 0.75rem 1rem; border-radius: 8px;
        background-color: rgba(76,175,80,0.15); border: 1px solid #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍲 Food Waste & Surplus Redistribution Tracker")
st.caption("Log surplus food, track donations, and reduce food waste - built with Python file handling + Streamlit.")

fm.ensure_file_exists()

# ---------------------------------------------------------------- sidebar --
with st.sidebar:
    st.header("📋 About this app")
    st.write(
        "Restaurants, stores, and households can log surplus edible food "
        "before it goes to waste, so it can be redistributed to NGOs or "
        "people in need."
    )
    ok, all_records = fm.read_all_records()
    if ok:
        total_qty = 0.0
        for r in all_records:
            try:
                total_qty += float(r.food.quantity_kg)
            except ValueError:
                pass
        st.metric("Total donations logged", len(all_records))
        st.metric("Total surplus food tracked", f"{total_qty:.1f} kg")
        pending = sum(1 for r in all_records if r.status == "Pending")
        st.metric("Pending pickups", pending)

    st.divider()
    st.caption(f"Data file: `data/donations.txt`")
    if st.button("📦 Create / Reset data file"):
        success, msg = fm.create_file()
        st.success(msg) if success else st.error(msg)

tabs = st.tabs(
    ["➕ Add Donation", "📄 View All", "🔍 Search", "✏️ Update", "🗑️ Delete", "🗄️ Backup"]
)

# ============================================================== ADD TAB ==
with tabs[0]:
    st.subheader("Log a new surplus food donation")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            donation_id = st.text_input("Donation ID*", placeholder="e.g. D001")
            donor_name = st.text_input("Donor / Household Name*", placeholder="e.g. Green Leaf Restaurant")
            food_item = st.text_input("Food Item*", placeholder="e.g. Cooked Rice")
        with col2:
            quantity = st.text_input("Quantity (kg)*", placeholder="e.g. 5.5")
            expiry_date = st.text_input("Expiry Date (dd-mm-yyyy)*", placeholder="e.g. 25-12-2026")
            contact = st.text_input("Contact (phone or email)*", placeholder="e.g. 9876543210")
        status = st.selectbox("Status", ["Pending", "Collected"])
        submitted = st.form_submit_button("Add Donation Record", use_container_width=True)

    if submitted:
        is_valid, message = val.validate_record(
            donation_id, donor_name, food_item, quantity, expiry_date, contact
        )
        if not is_valid:
            st.error(f"Validation error: {message}")
        else:
            record = DonationRecord(
                donation_id=donation_id.strip(),
                donor=Donor(name=donor_name.strip(), contact=contact.strip()),
                food=FoodItem(item_name=food_item.strip(), quantity_kg=quantity.strip(), expiry_date=expiry_date.strip()),
                status=status,
            )
            success, msg = fm.append_record(record)
            st.success(msg) if success else st.error(msg)

# ============================================================= VIEW TAB ==
with tabs[1]:
    st.subheader("All logged donations")
    success, data = fm.read_all_records()
    if not success:
        st.error(data)
    elif not data:
        st.info("No donation records yet. Add one from the 'Add Donation' tab.")
    else:
        df = pd.DataFrame([r.to_dict() for r in data])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Export as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="donations_export.csv",
            mime="text/csv",
        )

# =========================================================== SEARCH TAB ==
with tabs[2]:
    st.subheader("Search for a donation record")
    search_id = st.text_input("Enter Donation ID to search", key="search_box")
    if st.button("Search", key="search_btn"):
        if not search_id.strip():
            st.warning("Please enter a Donation ID.")
        else:
            success, result = fm.search_record(search_id)
            if success:
                st.markdown('<div class="success-box">Record found:</div>', unsafe_allow_html=True)
                st.json(result.to_dict())
            else:
                st.error(result)

# =========================================================== UPDATE TAB ==
with tabs[3]:
    st.subheader("Update an existing record")
    update_id = st.text_input("Donation ID to update", key="update_lookup")
    if st.button("Load record", key="load_btn"):
        success, result = fm.search_record(update_id)
        if success:
            st.session_state["record_to_update"] = result
            st.success("Record loaded below - edit and save.")
        else:
            st.error(result)
            st.session_state.pop("record_to_update", None)

    if "record_to_update" in st.session_state:
        rec = st.session_state["record_to_update"]
        with st.form("update_form"):
            col1, col2 = st.columns(2)
            with col1:
                donor_name = st.text_input("Donor / Household Name*", value=rec.donor.name)
                food_item = st.text_input("Food Item*", value=rec.food.item_name)
            with col2:
                quantity = st.text_input("Quantity (kg)*", value=str(rec.food.quantity_kg))
                expiry_date = st.text_input("Expiry Date (dd-mm-yyyy)*", value=rec.food.expiry_date)
            contact = st.text_input("Contact*", value=rec.donor.contact)
            status = st.selectbox("Status", ["Pending", "Collected"], index=0 if rec.status == "Pending" else 1)
            save = st.form_submit_button("Save Changes", use_container_width=True)

        if save:
            is_valid, message = val.validate_record(
                rec.donation_id, donor_name, food_item, quantity, expiry_date, contact
            )
            if not is_valid:
                st.error(f"Validation error: {message}")
            else:
                updated = DonationRecord(
                    donation_id=rec.donation_id,
                    donor=Donor(name=donor_name.strip(), contact=contact.strip()),
                    food=FoodItem(item_name=food_item.strip(), quantity_kg=quantity.strip(), expiry_date=expiry_date.strip()),
                    status=status,
                )
                success, msg = fm.update_record(rec.donation_id, updated)
                if success:
                    st.success(msg)
                    del st.session_state["record_to_update"]
                else:
                    st.error(msg)

# =========================================================== DELETE TAB ==
with tabs[4]:
    st.subheader("Delete a record")
    delete_id = st.text_input("Donation ID to delete", key="delete_box")
    confirm = st.checkbox("I confirm I want to permanently delete this record.")
    if st.button("Delete Record", type="primary"):
        if not delete_id.strip():
            st.warning("Please enter a Donation ID.")
        elif not confirm:
            st.warning("Please tick the confirmation checkbox first.")
        else:
            success, msg = fm.delete_record(delete_id)
            st.success(msg) if success else st.error(msg)

# =========================================================== BACKUP TAB ==
with tabs[5]:
    st.subheader("Backup the data file")
    st.write("Creates a timestamped copy of `donations.txt` inside `data/backups/`.")
    if st.button("Create Backup Now", use_container_width=True):
        success, msg = fm.backup_file()
        st.success(msg) if success else st.error(msg)

    st.divider()
    st.write("Existing backups:")
    backups = fm.list_backups()
    if backups:
        st.table(pd.DataFrame({"Backup file": backups}))
    else:
        st.info("No backups created yet.")
