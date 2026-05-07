import html
import os
import streamlit as st
import requests
from datetime import datetime, time

st.set_page_config(page_title="Network Tracker", page_icon="📇", layout="wide")

API_DEFAULT = os.environ.get("NETWORK_TRACKER_API_URL", "http://127.0.0.1:8000")

# Sidebar API config
st.sidebar.title("Network Tracker")
api_url = st.sidebar.text_input("API Base URL", API_DEFAULT)
try:
    requests.get(f"{api_url}/health", timeout=1).raise_for_status()
    st.sidebar.success("API connected")
except requests.RequestException:
    st.sidebar.error("API not reachable")

# Initialize session state for auth token and selected contact
if "token" not in st.session_state:
    st.session_state.token = None
if "selected_contact" not in st.session_state:
    st.session_state.selected_contact = None

st.title("Personal Network Tracker")
st.caption("Manage your contacts and interactions.")

st.markdown(
    """
    <style>
      .priority-badge, .follow-up-badge {
        border-radius: 999px;
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 700;
        line-height: 1;
        padding: 0.38rem 0.62rem;
        text-align: center;
        white-space: nowrap;
      }
      .priority-high { background: #fee2e2; color: #991b1b; }
      .priority-medium { background: #fef3c7; color: #92400e; }
      .priority-low { background: #dbeafe; color: #1e40af; }
      .priority-none { background: #f3f4f6; color: #4b5563; }
      .follow-up-yes { background: #ffedd5; color: #9a3412; }
      .follow-up-no { background: #f3f4f6; color: #6b7280; }
      .contact-header {
        color: #4b5563;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
      }
      .muted-cell {
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 1rem;
        font-weight: 400;
        line-height: 1.25;
      }
      .row-name {
        color: #ffffff;
        display: block;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 1rem;
        font-weight: 400;
        line-height: 1.2;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# Auth helper functions
def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def get_contacts(tag: str | None = None):
    params = {}
    if tag:
        params["tag"] = tag
    response = requests.get(f"{api_url}/contacts", params=params, timeout=5, headers=get_headers())
    response.raise_for_status()
    return response.json()


def get_contact(contact_id: int):
    response = requests.get(f"{api_url}/contacts/{contact_id}", timeout=5, headers=get_headers())
    response.raise_for_status()
    return response.json()


def create_contact(payload: dict):
    response = requests.post(f"{api_url}/contacts", json=payload, timeout=5, headers=get_headers())
    response.raise_for_status()
    return response.json()


def create_interaction(contact_id: int, payload: dict):
    response = requests.post(f"{api_url}/contacts/{contact_id}/interactions", json=payload, timeout=5, headers=get_headers())
    response.raise_for_status()
    return response.json()


def update_contact(contact_id: int, payload: dict):
    response = requests.put(f"{api_url}/contacts/{contact_id}", json=payload, timeout=5, headers=get_headers())
    response.raise_for_status()
    return response.json()


def delete_contact(contact_id: int):
    response = requests.delete(f"{api_url}/contacts/{contact_id}", timeout=5, headers=get_headers())
    response.raise_for_status()
    return response.json()


def update_interaction(contact_id: int, interaction_id: int, payload: dict):
    response = requests.put(
        f"{api_url}/contacts/{contact_id}/interactions/{interaction_id}",
        json=payload,
        timeout=5,
        headers=get_headers(),
    )
    response.raise_for_status()
    return response.json()


def delete_interaction(contact_id: int, interaction_id: int):
    response = requests.delete(
        f"{api_url}/contacts/{contact_id}/interactions/{interaction_id}",
        timeout=5,
        headers=get_headers(),
    )
    response.raise_for_status()
    return response.json()


def format_datetime(value: str):
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return value


def interaction_datetime_for_input(value: str) -> datetime:
    parsed = format_datetime(value)
    if isinstance(parsed, datetime) and parsed.year >= 1900:
        return parsed
    return datetime.now()


def combine_interaction_datetime(date_value, time_value) -> str:
    return datetime.combine(date_value, time_value).isoformat()


def safe_text(value) -> str:
    return html.escape(str(value or ""))


def priority_badge(priority: str | None) -> str:
    normalized = (priority or "none").lower()
    if normalized not in {"high", "medium", "low"}:
        normalized = "none"
    label = "None" if normalized == "none" else normalized.title()
    return f'<span class="priority-badge priority-{normalized}">{label}</span>'


def follow_up_badge(is_needed: bool) -> str:
    if is_needed:
        return '<span class="follow-up-badge follow-up-yes">Follow up</span>'
    return '<span class="follow-up-badge follow-up-no">Clear</span>'


def render_contact_detail(selected_contact_id: int) -> None:
    if st.button("← Back to contacts"):
        st.session_state.selected_contact = None
        st.session_state.editing_contact = False
        st.session_state.editing_interaction = None
        st.session_state.confirm_delete_contact = False
        st.rerun()

    try:
        contact = get_contact(selected_contact_id)
        st.header(contact["name"])

        priority = contact.get("priority") or "not set"
        company = contact.get("company") or ""
        title = contact.get("title") or ""
        st.caption(f"{priority.title()} priority" + (f" · {title}" if title else "") + (f" · {company}" if company else ""))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Email:** {contact.get('email') or ''}")
            st.write(f"**Phone:** {contact.get('phone') or ''}")
        with col2:
            st.write(f"**Tags:** {contact.get('tags') or ''}")
            st.write(f"**Created:** {format_datetime(contact.get('created_at'))}")
        with col3:
            if st.button("Edit Contact"):
                st.session_state.editing_contact = True
            if st.button("Delete Contact"):
                st.session_state.confirm_delete_contact = True

        notes = contact.get("notes")
        if notes:
            st.markdown("#### Notes")
            st.write(notes)

        if st.session_state.get("confirm_delete_contact"):
            st.warning("Are you sure you want to delete this contact?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, delete"):
                    try:
                        delete_contact(contact["id"])
                        st.success("Contact deleted")
                        st.session_state.selected_contact = None
                        st.session_state.confirm_delete_contact = False
                        st.rerun()
                    except requests.RequestException as exc:
                        st.error(f"Unable to delete contact: {exc}")
            with col2:
                if st.button("Cancel"):
                    st.session_state.confirm_delete_contact = False
                    st.rerun()

        if st.session_state.get("editing_contact"):
            with st.form("edit_contact_form"):
                name = st.text_input("Name", value=contact.get("name") or "")
                title = st.text_input("Title", value=contact.get("title") or "")
                company = st.text_input("Company", value=contact.get("company") or "")
                email = st.text_input("Email", value=contact.get("email") or "")
                phone = st.text_input("Phone", value=contact.get("phone") or "")
                priorities = ["", "low", "medium", "high"]
                priority_value = contact.get("priority") if contact.get("priority") in priorities else ""
                priority = st.selectbox("Priority", priorities, index=priorities.index(priority_value or ""))
                tags_input = st.text_input("Tags (comma-separated)", value=contact.get("tags") or "")
                notes = st.text_area("Notes", value=contact.get("notes") or "")
                submitted_update = st.form_submit_button("Save contact")

                if submitted_update:
                    if not name.strip():
                        st.error("Name is required")
                    else:
                        payload = {
                            "name": name.strip(),
                            "title": title.strip() or None,
                            "company": company.strip() or None,
                            "email": email.strip() or None,
                            "phone": phone.strip() or None,
                            "priority": priority.strip() or None,
                            "tags": tags_input.strip() or None,
                            "notes": notes.strip() or None,
                        }
                        try:
                            update_contact(selected_contact_id, payload)
                            st.success("Contact updated")
                            st.session_state.editing_contact = False
                            st.rerun()
                        except requests.RequestException as exc:
                            st.error(f"Unable to update contact: {exc}")

        st.subheader("Interactions")
        interactions = contact.get("interactions", [])
        if interactions:
            for interaction in interactions:
                interaction_date = format_datetime(interaction.get("date"))
                with st.expander(f"{interaction_date} - {interaction.get('type', 'note')}", expanded=False):
                    st.write(f"**Channel:** {interaction.get('channel', '')}")
                    st.write(f"**Notes:** {interaction.get('notes', '')}")
                    st.write(f"**Follow-up:** {interaction.get('follow_up', False)}")
                    if interaction.get("follow_up_notes"):
                        st.write(f"**Follow-up notes:** {interaction.get('follow_up_notes')}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit", key=f"edit_interaction_{interaction['id']}"):
                            st.session_state.editing_interaction = interaction["id"]
                    with col2:
                        if st.button("Delete", key=f"delete_interaction_{interaction['id']}"):
                            try:
                                delete_interaction(selected_contact_id, interaction["id"])
                                st.success("Interaction deleted")
                                st.rerun()
                            except requests.RequestException as exc:
                                st.error(f"Unable to delete interaction: {exc}")

                    if st.session_state.get("editing_interaction") == interaction["id"]:
                        with st.form(f"edit_interaction_form_{interaction['id']}"):
                            existing_date = interaction_datetime_for_input(interaction.get("date"))
                            interaction_date = st.date_input("Date", value=existing_date.date(), key=f"date_{interaction['id']}")
                            interaction_time = st.time_input("Time", value=existing_date.time().replace(microsecond=0), key=f"time_{interaction['id']}")
                            interaction_type = st.text_input("Type", value=interaction.get("type", ""), key=f"type_{interaction['id']}")
                            channel = st.text_input("Channel", value=interaction.get("channel", ""), key=f"channel_{interaction['id']}")
                            notes = st.text_area("Notes", value=interaction.get("notes", ""), key=f"notes_{interaction['id']}")
                            follow_up = st.checkbox("Mark as follow-up", value=interaction.get("follow_up", False), key=f"follow_up_{interaction['id']}")
                            follow_up_notes = None
                            if follow_up:
                                follow_up_notes = st.text_area(
                                    "Follow-up notes",
                                    value=interaction.get("follow_up_notes") or "",
                                    key=f"follow_up_notes_{interaction['id']}",
                                )
                            submitted_interaction = st.form_submit_button("Update interaction", key=f"update_interaction_{interaction['id']}")

                            if submitted_interaction:
                                payload = {
                                    "date": combine_interaction_datetime(interaction_date, interaction_time),
                                    "type": interaction_type.strip() or "note",
                                    "channel": channel.strip() or None,
                                    "notes": notes.strip() or None,
                                    "follow_up": follow_up,
                                    "follow_up_notes": follow_up_notes.strip() if follow_up and follow_up_notes else None,
                                }
                                try:
                                    update_interaction(selected_contact_id, interaction["id"], payload)
                                    st.success("Interaction updated")
                                    st.session_state.editing_interaction = None
                                    st.rerun()
                                except requests.RequestException as exc:
                                    st.error(f"Unable to update interaction: {exc}")
        else:
            st.info("No interactions yet.")

        with st.expander("Add interaction", expanded=False):
            with st.form("create_interaction_form"):
                interaction_date = st.date_input("Date", value=datetime.now().date())
                interaction_time = st.time_input("Time", value=time(hour=9))
                interaction_type = st.text_input("Type", value="note")
                channel = st.text_input("Channel")
                notes = st.text_area("Notes")
                follow_up = st.checkbox("Mark as follow-up", value=False)
                follow_up_notes = None
                if follow_up:
                    follow_up_notes = st.text_area("Follow-up notes")
                submitted_interaction = st.form_submit_button("Save interaction")

                if submitted_interaction:
                    payload = {
                        "date": combine_interaction_datetime(interaction_date, interaction_time),
                        "type": interaction_type.strip() or "note",
                        "channel": channel.strip() or None,
                        "notes": notes.strip() or None,
                        "follow_up": follow_up,
                        "follow_up_notes": follow_up_notes.strip() if follow_up and follow_up_notes else None,
                    }
                    try:
                        create_interaction(selected_contact_id, payload)
                        st.success("Interaction added")
                        st.rerun()
                    except requests.RequestException as exc:
                        st.error(f"Unable to add interaction: {exc}")
    except requests.RequestException as exc:
        st.error(f"Unable to load contact details: {exc}")


# Login / Signup
if not st.session_state.token:
    st.markdown("### Sign in or create an account")
    
    auth_mode = st.radio("Choose action", ["Log in", "Sign up"])
    
    with st.form("auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not username or not password:
                st.error("Username and password are required")
            else:
                endpoint = "login" if auth_mode == "Log in" else "signup"
                try:
                    response = requests.post(
                        f"{api_url}/auth/{endpoint}",
                        json={"username": username, "password": password},
                        timeout=5
                    )
                    response.raise_for_status()
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]
                    st.session_state.username = username  # Store username
                    st.success(f"Successfully {'logged in' if auth_mode == 'Log in' else 'signed up'}!")
                    st.rerun()
                except requests.exceptions.RequestException as exc:
                    st.error(f"Authentication failed: {exc}")
else:
    # Logged in - show main app
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Logged in**")
    with col2:
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.selected_contact = None
            st.rerun()
    
    st.markdown("---")

    selected_contact_id = st.session_state.selected_contact
    if selected_contact_id is not None:
        render_contact_detail(selected_contact_id)
        st.stop()
    
    with st.expander("Search and filter contacts", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            tag = st.text_input("Filter by tag", placeholder="e.g. Sales and Trading, Boston")
        with col2:
            search = st.text_input("Search name or company")
        
        contacts = []
        try:
            contacts = get_contacts(tag.strip() or None)
        except requests.RequestException as exc:
            st.error(f"Unable to load contacts: {exc}")

        if search:
            search_lower = search.lower()
            contacts = [
                c
                for c in contacts
                if search_lower in c.get("name", "").lower()
                or search_lower in (c.get("company") or "").lower()
                or search_lower in (c.get("tags") or "").lower()
            ]

        st.markdown("### Contacts")
        if contacts:
            st.markdown(f'<div class="muted-cell">Contact total: {len(contacts)}</div>', unsafe_allow_html=True)

            header_cols = st.columns([1.1, 2, 2, 2, 1.3, 1, 1, 1])
            headers = ["Priority", "Name", "Company", "Tags", "Follow-up", "", "", ""]
            for column, label in zip(header_cols, headers):
                with column:
                    st.markdown(f'<div class="contact-header">{label}</div>', unsafe_allow_html=True)

            for contact in contacts:
                with st.container(border=True):
                    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.1, 2, 2, 2, 1.3, 1, 1, 1])
                    with col1:
                        st.markdown(priority_badge(contact.get("priority")), unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="row-name">{safe_text(contact["name"])}</div>', unsafe_allow_html=True)
                    with col3:
                        st.markdown(f'<span class="muted-cell">{safe_text(contact.get("company"))}</span>', unsafe_allow_html=True)
                    with col4:
                        st.markdown(f'<span class="muted-cell">{safe_text(contact.get("tags"))}</span>', unsafe_allow_html=True)
                    with col5:
                        st.markdown(follow_up_badge(bool(contact.get("follow_up_needed"))), unsafe_allow_html=True)
                    with col6:
                        if st.button("View", key=f"view_{contact['id']}"):
                            st.session_state.selected_contact = contact['id']
                            st.rerun()
                    with col7:
                        if st.button("Edit", key=f"edit_list_{contact['id']}"):
                            st.session_state.editing_contact = True
                            st.session_state.selected_contact = contact['id']
                            st.rerun()
                    with col8:
                        if st.button("Delete", key=f"delete_list_{contact['id']}"):
                            st.session_state.confirm_delete_contact = True
                            st.session_state.selected_contact = contact["id"]
                            st.rerun()
            st.markdown("---")
        else:
            st.info("No contacts found. Add one below or change your filter.")

    with st.expander("Add a new contact", expanded=False):
        with st.form("create_contact_form"):
            name = st.text_input("Name")
            title = st.text_input("Title")
            company = st.text_input("Company")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            priority = st.selectbox("Priority", ["", "low", "medium", "high"])
            tags_input = st.text_input("Tags (comma-separated)")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Create contact")

            if submitted:
                if not name.strip():
                    st.error("Name is required")
                else:
                    payload = {
                        "name": name.strip(),
                        "title": title.strip() or None,
                        "company": company.strip() or None,
                        "email": email.strip() or None,
                        "phone": phone.strip() or None,
                        "priority": priority.strip() or None,
                        "tags": tags_input.strip() or None,
                        "notes": notes.strip() or None,
                    }
                    try:
                        created = create_contact(payload)
                        st.success(f"Contact created: {created['name']}")
                        st.rerun()
                    except requests.RequestException as exc:
                        st.error(f"Unable to create contact: {exc}")
