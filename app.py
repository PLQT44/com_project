import csv
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STATIC_FOLDER'] = './static'
db = SQLAlchemy(app)

# Models
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    reserved_by = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)

    def __repr__(self):
        return self.name

# Initialize Database and Load Static Data
@app.before_request
def setup_database():
    db.create_all()

    # Load users.csv
    users_csv = os.path.join(app.config['STATIC_FOLDER'], 'users.csv')
    if os.path.exists(users_csv):
        load_members_from_csv(users_csv)

    # Load points.csv
    points_csv = os.path.join(app.config['STATIC_FOLDER'], 'points.csv')
    if os.path.exists(points_csv):
        load_locations_from_csv(points_csv)

# API Endpoints
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'GET':
        locations = Location.query.all()
        return jsonify([{
            'id': loc.id,
            'name': loc.name,
            'address': loc.address,
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'reserved_by': loc.reserved_by
        } for loc in locations])
    elif request.method == 'POST':
        data = request.json
        # Validate duplicates
        if Location.query.filter_by(name=data['name'], address=data['address']).first():
            return jsonify({'message': 'Location already exists'}), 400

        location = Location(
            name=data['name'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        db.session.add(location)
        db.session.commit()
        return jsonify({'message': 'Location added successfully'}), 201

@app.route('/reserved_locations', methods=['GET'])
def reserved_locations():
    locations = Location.query.filter(Location.reserved_by.isnot(None)).all()
    result = []
    for loc in locations:
        member = Member.query.get(loc.reserved_by)
        result.append({
            'location': loc.name,
            'address': loc.address,
            'reserved_by': f"{member.first_name} {member.last_name}" if member else "Unknown"
        })
    return jsonify(result)

@app.route('/reserve', methods=['POST'])
def reserve():
    data = request.json
    location = Location.query.get(data['location_id'])
    if location and not location.reserved_by:
        location.reserved_by = data['member_id']
        db.session.commit()
        return jsonify({'message': 'Location reserved successfully'})
    return jsonify({'message': 'Location already reserved or not found'}), 400

@app.route('/members', methods=['POST'])
def members():
    data = request.json
    # Validate duplicates
    if Member.query.filter_by(first_name=data['first_name'], last_name=data['last_name']).first():
        return jsonify({'message': 'Member already exists'}), 400

    member = Member(
        first_name=data['first_name'],
        last_name=data['last_name'],
        address=data.get('address', '')
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({'id': member.id}), 201

# Helper Functions
def load_members_from_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not Member.query.filter_by(first_name=row['first_name'], last_name=row['last_name']).first():
                member = Member(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    address=row.get('address', '')
                )
                db.session.add(member)
        db.session.commit()

def load_locations_from_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not Location.query.filter_by(name=row['name'], address=row['address']).first():
                location = Location(
                    name=row['name'],
                    address=row['address'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude'])
                )
                db.session.add(location)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
