import requests
from flask import Flask, request, jsonify
import random

# раздел 1
print("раздел 1")
req = requests.get("http://127.0.0.1:5000/number/?param=10")
print("1.1")
print(req.text)

response2 = requests.post("http://127.0.0.1:5000/number/", json={"jsonParam": 2})
print("1.2")
print(response2.text)

response3 = requests.delete("http://127.0.0.1:5000/number/")
print("1.3")
print(response3.text)

# раздел 2
print("раздел 2")
# 2.1
param = random.randint(1, 10)
response = requests.get(f"http://127.0.0.1:5000/number/?param={param}")
data = response.json()
get_number = data["result"]
get_operation = random.choice(["+", "-", "*", "/"])
print(f"GET число: {get_number} и операция: {get_operation}")

2.2
json_param = random.randint(1, 10)
response = requests.post("http://127.0.0.1:5000/number/",
                         json={"jsonParam": json_param}, headers={"content-type": "application/json"})
data = response.json()
post_number = data["result"]
post_operation = data["operation"]
print(f"POST число: {post_number} и операция: {post_operation}")

2.3
response = requests.delete("http://127.0.0.1:5000/number/")
data = response.json()
delete_number = data["result"]
delete_operation = data["operation"]
print(f"DELETE число: {delete_number} и операция: {delete_operation}")

# 2.4
final_result = 0

if get_operation == "*" or get_operation == "/":
    if get_operation == "*":
        final_result = get_number * post_number
    elif get_operation == "/":
        final_result = get_number / post_number

    if post_operation == "+":
        final_result = final_result + delete_number
    elif post_operation == "-":
        final_result = final_result - delete_number
    elif post_operation == "*":
        final_result = final_result * delete_number
    elif post_operation == "/":
        final_result = final_result / delete_number

elif get_operation == "+" or get_operation == "-":
    if post_operation == "*" or post_operation == "/":
        if post_operation == "*":
            final_result = post_number * delete_number
        elif post_operation == "/":
            final_result = post_number / delete_number

        if get_operation == "+":
            final_result = get_number + final_result
        elif get_operation == "-":
            final_result = get_number - final_result
        elif get_operation == "*":
            final_result = get_number * final_result
        elif get_operation == "/":
            final_result = get_number / final_result

    elif post_operation == "+" or post_operation == "-":
        if get_operation == "+":
            final_result = get_number + post_number
        elif get_operation == "-":
            final_result = get_number - post_number
        elif get_operation == "*":
            final_result = get_number * post_number
        elif get_operation == "/":
            final_result = get_number / post_number

        if post_operation == "+":
            final_result = final_result + delete_number
        elif post_operation == "-":
            final_result = final_result - delete_number

final_result = int(final_result)
print(f"Результат: {final_result}")


# раздел 3
print("раздел 3")
# 3.1


