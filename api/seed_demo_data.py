"""
Script to populate the database with demo/sample data for the jail roster.
"""
import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "https://jailroster.shakerpd.com/api"

# Login credentials
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

# Demo inmate records
DEMO_RECORDS = [
    {
        "name": "John Smith",
        "oca_number": "2024-001234",
        "arrest_date_time": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M"),
        "charges": "Theft, Possession",
        "bond": "$5,000",
        "jail_location": "Main",
        "cell": "A-101",
        "court_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "holders_notes": "First offense, cooperative",
        "release_date_time": None
    },
    {
        "name": "Jane Doe",
        "oca_number": "2024-001235",
        "arrest_date_time": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M"),
        "charges": "DUI, Reckless Driving",
        "bond": "$2,500",
        "jail_location": "Main",
        "cell": "B-205",
        "court_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "holders_notes": "Awaiting arraignment",
        "release_date_time": None
    },
    {
        "name": "Michael Johnson",
        "oca_number": "2024-001236",
        "arrest_date_time": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
        "charges": "Assault, Disorderly Conduct",
        "bond": "$10,000",
        "jail_location": "Main",
        "cell": "C-302",
        "court_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "holders_notes": "Requires monitoring",
        "release_date_time": None
    },
    {
        "name": "Sarah Williams",
        "oca_number": "2024-001237",
        "arrest_date_time": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
        "charges": "Shoplifting",
        "bond": "$1,000",
        "jail_location": "Main",
        "cell": "B-103",
        "court_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "holders_notes": "Bond posted, pending release",
        "release_date_time": None
    },
    {
        "name": "Robert Brown",
        "oca_number": "2024-001238",
        "arrest_date_time": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M"),
        "charges": "Burglary",
        "bond": "$15,000",
        "jail_location": "Main",
        "cell": "A-205",
        "court_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "holders_notes": "Released on recognizance",
        "release_date_time": (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M")
    }
]

def main():
    """Populate the database with demo data."""
    print("🔐 Logging in...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Login
    login_response = session.post(
        f"{BASE_URL}/auth/login",
        json=LOGIN_DATA,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    print("✅ Login successful!")
    print(f"\n📝 Adding {len(DEMO_RECORDS)} demo records...")
    
    # Add each demo record
    success_count = 0
    for i, record in enumerate(DEMO_RECORDS, 1):
        print(f"\n[{i}/{len(DEMO_RECORDS)}] Adding: {record['name']}")
        
        response = session.post(
            f"{BASE_URL}/roster",
            json=record,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print(f"  ✅ Added successfully")
            success_count += 1
        else:
            print(f"  ❌ Failed: {response.text}")
    
    print(f"\n🎉 Done! Successfully added {success_count}/{len(DEMO_RECORDS)} records")
    print(f"\n🌐 Visit https://jailroster.shakerpd.com to see the demo data!")

if __name__ == "__main__":
    main()
