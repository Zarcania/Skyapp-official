#!/usr/bin/env python3
"""
Focused test for the remaining issues in enhanced endpoints
"""

import requests
import json

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"

def test_remaining_issues():
    session = requests.Session()
    
    # Setup authentication
    response = session.post(f"{BACKEND_URL}/init-sample-data")
    login_data = {"email": "tech@search-app.fr", "password": "tech123"}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data["access_token"]
        session.headers.update({"Authorization": f"Bearer {auth_token}"})
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        return
    
    # Test 1: Share-to-Bureau Error Handling
    print("\n🔍 Testing Share-to-Bureau Error Handling")
    share_data = {"search_ids": []}
    response = session.post(f"{BACKEND_URL}/reports/share-to-bureau", json=share_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test 2: Quote Conversion Restrictions
    print("\n🔍 Testing Quote Conversion Restrictions")
    
    # Create client and quote
    client_data = {
        "nom": "Test Client",
        "email": "test@client.com",
        "telephone": "01 23 45 67 89"
    }
    client_response = session.post(f"{BACKEND_URL}/clients", json=client_data)
    
    if client_response.status_code == 200:
        client = client_response.json()
        
        quote_data = {
            "client_id": client["id"],
            "title": "Test Quote",
            "description": "Test description",
            "amount": 1000.0
        }
        quote_response = session.post(f"{BACKEND_URL}/quotes", json=quote_data)
        
        if quote_response.status_code == 200:
            quote = quote_response.json()
            print(f"Created quote with status: {quote.get('status')}")
            
            # Try to convert DRAFT quote (should fail)
            convert_response = session.post(f"{BACKEND_URL}/quotes/{quote['id']}/convert-to-worksite")
            print(f"Conversion status: {convert_response.status_code}")
            print(f"Conversion response: {convert_response.text}")
    
    # Test 3: Search Status Update
    print("\n🔍 Testing Search Status Update with SHARED_TO_BUREAU")
    
    # Create a search
    form_data = {
        'location': 'Test Location',
        'description': 'Test description',
        'observations': 'Test observations',
        'latitude': '48.8566',
        'longitude': '2.3522'
    }
    search_response = session.post(f"{BACKEND_URL}/searches", data=form_data)
    
    if search_response.status_code == 200:
        search = search_response.json()
        print(f"Created search: {search['id']}")
        
        # Test share-to-bureau with this search
        share_data = {"search_ids": [search["id"]]}
        share_response = session.post(f"{BACKEND_URL}/reports/share-to-bureau", json=share_data)
        print(f"Share status: {share_response.status_code}")
        print(f"Share response: {share_response.text}")
        
        # Check if search status was updated
        get_response = session.get(f"{BACKEND_URL}/searches/{search['id']}")
        if get_response.status_code == 200:
            updated_search = get_response.json()
            print(f"Updated search status: {updated_search.get('status')}")
        else:
            print(f"Failed to get updated search: {get_response.text}")

if __name__ == "__main__":
    test_remaining_issues()