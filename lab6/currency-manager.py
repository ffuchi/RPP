from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    database="rpp6",
    user="admin_rpp6",
    password="123",
    host="127.0.0.1")
cursor = conn.cursor()

@app.route("/load", methods=["POST"])
def load_currency():
    currency_name = request.json["currency_name"].upper()
    currency_rate = request.json["currency_rate"]

    cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))

    if cursor.fetchone():
        return jsonify({"message": "Валюта уже существует"}), 400

    cursor.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (currency_name, currency_rate))
    conn.commit()

    return jsonify({"message": "Валюта успешно загружена"}), 200

@app.route("/update_currency", methods=["POST"])
def update_currency():
    currency_name = request.json["currency_name"].upper()
    new_currency_rate = request.json["currency_rate"]

    cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))

    if not cursor.fetchone():
        return jsonify({"message": "Валюта не найдена"}), 404

    cursor.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (new_currency_rate, currency_name))
    conn.commit()

    return jsonify({"message": "Успешно обновлен курс валюты"}), 200

@app.route("/delete_currency", methods=["POST"])
def delete_currency():
    currency_name = request.json["currency_name"].upper()

    cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))

    if not cursor.fetchone():
        return jsonify({"message": "Валюта не найдена"}), 404

    cursor.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
    conn.commit()

    return jsonify({"message": "Валюта успешно удалена"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
