from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# 1.1
@app.route("/number/", methods=["GET"])
def get_number():
    param = int(request.args.get("param"))
    random_number = random.randint(1, 100)
    response = {"result": random_number * param}
    return jsonify(response)

# 1.2
@app.route("/number/", methods=["POST"])
def post_number():
    data = request.get_json()
    json_param = data.get("jsonParam")
    random_number = random.randint(1, 100)
    operation = random.choice(["+", "-", "*", "/"])
    result = 0

    if operation == "+":
        result = json_param + random_number
    elif operation == "-":
        result = json_param - random_number
    elif operation == "*":
        result = json_param * random_number
    elif operation == "/":
        result = json_param / random_number

    response = {"result": result, "operation": operation}
    return jsonify(response)

# 1.3
@app.route("/number/", methods=["DELETE"])
def delete_number():
    random_number = random.randint(1, 100)
    operation = random.choice(["+", "-", "*", "/"])
    response = {"result": random_number, "operation": operation}
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)


