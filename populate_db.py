# populate_db.py
from app import app, db, Member, Location
import csv
import os

def populate_from_csv():
    with app.app_context():
         # Create all tables first
        print("Creating database tables...")
        db.create_all()
        
        print("Populating from CSV files...")
        # Load users.csv
        users_path = os.path.join('static', 'users.csv')
        with open(users_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                member = Member(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    address=row.get('address', '')
                )
                db.session.add(member)
        
        # Load points.csv
        points_path = os.path.join('static', 'points.csv')
        with open(points_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                location = Location(
                    name=row['name'],
                    city=row['city'],
                    address=row['address'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude'])
                )
                db.session.add(location)
        
        db.session.commit()
        print("Database populated successfully!")

if __name__ == "__main__":
    try:
        populate_from_csv()
    except Exception as e:
        print(f"Error: {e}")