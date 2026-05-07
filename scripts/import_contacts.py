#!/usr/bin/env python
"""
Import contacts and interactions from Network.xlsx into the app database.

Usage:
  cd /Users/nickmartin/codingprojects/network_tracker
  source .venv/bin/activate
  python scripts/import_contacts.py
"""

import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

# Add the app directory to the path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import auth, crud, database, models


def parse_date(value):
    """Try to parse a date string or datetime object."""
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value
    try:
        return pd.to_datetime(value)
    except (ValueError, TypeError):
        return None


def import_contacts():
    """Import contacts from Network.xlsx."""
    excel_path = project_root / "Network.xlsx"
    
    if not excel_path.exists():
        print(f"Error: {excel_path} not found")
        sys.exit(1)
    
    print(f"Reading {excel_path}...")
    df = pd.read_excel(excel_path)
    
    print(f"Found {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}\n")
    
    # Initialize database
    database.init_db()
    
    # Create or get user
    with database.get_session() as session:
        username = "nick"
        password = "password123"
        
        user = auth.create_user(session, username, password)
        if not user:
            print(f"User '{username}' already exists, using existing user")
            user = auth.get_user_by_username(session, username)
        else:
            print(f"Created user '{username}'")
        
        user_id = user.id
    
    imported = 0
    skipped = 0
    
    for idx, row in df.iterrows():
        name = row.get("Name", "").strip() if pd.notna(row.get("Name")) else None
        
        if not name:
            print(f"Row {idx}: Skipping empty name")
            skipped += 1
            continue
        
        # Map columns
        position = row.get("Position", "").strip() if pd.notna(row.get("Position")) else None
        industry = row.get("Industry", "").strip() if pd.notna(row.get("Industry")) else None
        location = row.get("Location", "").strip() if pd.notna(row.get("Location")) else None
        conversation_notes = row.get("Conversation Notes", "").strip() if pd.notna(row.get("Conversation Notes")) else None
        last_spoken_to = row.get("Last Spoken To")
        category = row.get("Most Important, follow up Weekly/Biweekly", "").strip() if pd.notna(row.get("Most Important, follow up Weekly/Biweekly")) else None
        
        # Build tags: combine industry, location, and category
        tags_list = []
        if industry:
            tags_list.append(industry)
        if location:
            tags_list.append(location)
        if category:
            tags_list.append(category)
        tags = ", ".join(tags_list) if tags_list else None
        
        # Build notes: combine position and any conversation notes
        notes_list = []
        if position:
            notes_list.append(f"Position: {position}")
        if conversation_notes:
            notes_list.append(conversation_notes)
        notes = "\n".join(notes_list) if notes_list else None
        
        # Create contact
        contact_data = models.Contact(
            user_id=user_id,
            name=name,
            title=position if position else None,
            company=industry if industry else None,
            tags=tags,
            notes=notes,
        )
        
        try:
            contact = crud.create_contact(contact_data)
            print(f"Row {idx}: Created contact '{name}' (ID: {contact.id})")
            
            # Create interaction if we have conversation notes and a date
            if (conversation_notes or last_spoken_to) and pd.notna(last_spoken_to):
                interaction_date = parse_date(last_spoken_to)
                if interaction_date:
                    interaction_data = models.Interaction(
                        contact_id=contact.id,
                        date=interaction_date,
                        type="conversation",
                        notes=conversation_notes if conversation_notes else None,
                    )
                    crud.create_interaction(contact.id, interaction_data)
                    print(f"  ↳ Added interaction from {interaction_date.date()}")
            
            imported += 1
        except Exception as e:
            print(f"Row {idx}: Error creating contact '{name}': {e}")
            skipped += 1
    
    print(f"\n✅ Import complete: {imported} contacts imported, {skipped} skipped")
    print(f"\n📝 Login credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")


if __name__ == "__main__":
    import_contacts()
