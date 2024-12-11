import psycopg2

conn = psycopg2.connect(
    dbname="my_map_db",
    user="flask_user",
    password="Hohenbourg_720",
    host="34.163.125.127"
)
print("Connected successfully")