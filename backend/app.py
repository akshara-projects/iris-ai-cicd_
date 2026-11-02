from flask import Flask, request, jsonify
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import psycopg2
import os
import time

app = Flask(__name__)

# Load Iris dataset
iris = load_iris()

# Train machine learning model
model = RandomForestClassifier(random_state=42)
model.fit(iris.data, iris.target)


# Database connection
def get_db_connection():

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "irisdb"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin123"),
        port=5432
    )


# Wait for database and create table
def initialize_database():

    for attempt in range(15):

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    sepal_length FLOAT,
                    sepal_width FLOAT,
                    petal_length FLOAT,
                    petal_width FLOAT,
                    prediction VARCHAR(50)
                )
            """)

            connection.commit()
            cursor.close()
            connection.close()

            print("Database connected successfully")
            return

        except psycopg2.OperationalError:
            print("Waiting for database...")
            time.sleep(2)

    raise RuntimeError("Could not connect to database")


# Home route
@app.route("/")
def home():
    return "Iris AI Backend is Running!"


# Health route
@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


# Prediction route
@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        values = [
            float(data["sepal_length"]),
            float(data["sepal_width"]),
            float(data["petal_length"]),
            float(data["petal_width"])
        ]

        result = model.predict([values])[0]
        flower_name = iris.target_names[result]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO predictions
            (sepal_length, sepal_width, petal_length,
             petal_width, prediction)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            values[0],
            values[1],
            values[2],
            values[3],
            flower_name
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "prediction": flower_name,
            "message": "Prediction saved successfully"
        })

    except (ValueError, KeyError, TypeError) as error:

        return jsonify({"error": str(error)}), 400

    except psycopg2.Error as error:

        return jsonify({"error": "Database operation failed"}), 500


# Start application
if __name__ == "__main__":

    initialize_database()

    app.run(
        host="0.0.0.0",
        port=5000
    )
