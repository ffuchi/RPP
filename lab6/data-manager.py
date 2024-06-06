from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    database="rpp6",
    user="admin_rpp6",
    password="123",
    host="127.0.0.1")
cursor = conn.cursor()

@app.route("/currencies", methods=["GET"])
def get_currencies():
    with conn.cursor() as cursor:
        cursor.execute("SELECT currency_name, rate FROM currencies")
        currencies = cursor.fetchall()

        if not currencies:
            response = "Нет сохраненных валют!"
            return jsonify({'message': response}), 400
        else:
            report = "Сохраненные валюты:\n"
            for currency in currencies:
                currency_name, rate = currency  # Распаковываем кортеж
                report += f"1 {currency_name} = {rate} РУБЛЕЙ\n"
            return jsonify({'message': report}), 200


@app.route("/convert", methods=["GET"])
def convert_currency():
    currency_name = request.args.get('currency_name')
    amount = float(request.args.get("amount"))

    with conn.cursor() as cursor:
        cursor.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
        currency_data = cursor.fetchone()
        if not currency_data:
            return jsonify({'message': 'Валюта не найдена'}), 404
        else:
            res = amount * float(currency_data[0])
            res = f"{res:.2f}"
            return jsonify({'message': res}), 200



if __name__ == "__main__":
    app.run(debug=True, port=5002)








