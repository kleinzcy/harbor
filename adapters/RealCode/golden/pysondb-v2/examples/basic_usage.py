#!/usr/bin/env python3
"""
Basic usage example for pysonDB-v2.
"""
import os
from pysondb import PysonDB

def main():
    # Create or load a database
    db = PysonDB('example.db.json')

    # Add some records
    alice_id = db.add({'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
    bob_id = db.add({'name': 'Bob', 'age': 25, 'email': 'bob@example.com'})
    charlie_id = db.add({'name': 'Charlie', 'age': 35, 'email': 'charlie@example.com'})

    print(f"Added records with IDs: {alice_id}, {bob_id}, {charlie_id}")

    # Retrieve all records
    all_records = db.get_all()
    print(f"\nTotal records: {len(all_records)}")

    # Query records
    adults = db.get_by_query(lambda x: x['age'] >= 30)
    print(f"\nAdults (age >= 30): {len(adults)}")
    for record_id, record in adults.items():
        print(f"  - {record['name']} ({record['age']})")

    # Update a record
    db.update_by_id(alice_id, {'age': 31})
    updated = db.get_by_id(alice_id)
    print(f"\nUpdated Alice's age to: {updated['age']}")

    # Select specific fields
    names_only = db.get_all_select_keys(['name', 'email'])
    print("\nNames and emails:")
    for record_id, record in names_only.items():
        print(f"  - {record['name']}: {record.get('email', 'N/A')}")

    # Add a new field to all records
    db.add_new_key('subscription', 'free')
    print("\nAdded 'subscription' field to all records")

    # Delete a record
    db.delete_by_id(bob_id)
    remaining = db.get_all()
    print(f"\nAfter deletion: {len(remaining)} records remaining")

    # Purge the database
    db.purge()
    print(f"\nPurged database. Total records: {len(db.get_all())}")

    # Clean up
    os.remove('example.db.json')
    print("\nCleaned up example database file.")

if __name__ == '__main__':
    main()