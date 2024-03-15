# ЗАДАНИЕ 4
numbers_str = input("Введите последовательность целых чисел: ")

total_sum = 0
count = 0
i = 0

while i < len(numbers_str):
    num = ""
    while i < len(numbers_str) and numbers_str[i] != " ":
        num += numbers_str[i]
        i += 1
    if num:
        total_sum += int(num)
        count += 1
    i += 1
print("Сумма всех чисел:", total_sum)
print("Количество всех чисел:", count)