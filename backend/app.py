# app.py
from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'kubefortunes')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

FORTUNES = [
    "Kubernetes loves YAML, and so will you!",
    "Don't forget to label your pods – it's like naming your pets.",
    "Rolling updates are smoother than reboots.",
    "Secrets should stay secret – base64 encoding is not encryption!",
    "Always specify resource requests – or risk the wrath of the scheduler.",
    "Your pods may fail, but Kubernetes won't stop trying.",
    "Taints and tolerations: the matchmaking service of Kubernetes.",
    "ConfigMaps: Keeping hardcoded configs out of your containers since 2015.",
    "Persistent Volumes: Where your data stays even if your pods don’t.",
    "Kubernetes is like magic – until you forget to check the logs.",
]

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def initialize_database():
    """Create the fortunes table if it doesn't exist and populate it."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Create table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fortunes (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL
    )
    ''')
    connection.commit()

    cursor.execute('SELECT COUNT(*) FROM fortunes')
    count = cursor.fetchone()[0]

    if count == 0:
        for fortune in FORTUNES:
            cursor.execute('INSERT INTO fortunes (text) VALUES (%s)', (fortune,))
        connection.commit()
        print("Inserted default fortunes into the database.")

    cursor.close()
    connection.close()

@app.route('/fortune', methods=['GET'])
def get_fortune():
    """Return a random Kubernetes fortune."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT text FROM fortunes ORDER BY RANDOM() LIMIT 1')
        fortune = cursor.fetchone()
        cursor.close()
        connection.close()
        return jsonify({'fortune': fortune[0] if fortune else 'No fortunes found!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Initializing database...")
    initialize_database()
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000)