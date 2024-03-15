# ЗАДАНИЕ 3.5
numbers_str = input("Введите последовательность целых чисел: ")
i = 0
array = []
while i < len(numbers_str):
    num = ""
    while i < len(numbers_str) and numbers_str[i] != " ":
        num += numbers_str[i]
        i += 1
    if num:  # Проверка, не является ли num пустой строкой
        array.append(int(num))  # Добавление целочисленное значение к массиву
    i += 1
print("Массив:", array)

# вывод пар отрицательных чисел, стоящих рядом
negative_pairs = []
for j in range(len(array) - 1):
    if int(array[j]) < 0 and int(array[j + 1]) < 0:
        negative_pairs.append((int(array[j]), int(array[j + 1])))
print("Пары отрицательных чисел:", negative_pairs)

# Удаление всех одинаковых повторяющихся чисел
unique_array = list(set(array))
print("Массив без повторений:", unique_array)

# Удаление всех одинаковых повторяющихся пар отрицательных чисел
unique_negative_pairs = list(set(negative_pairs))
print("Пары отрицательных чисел без повторений:", unique_negative_pairs)