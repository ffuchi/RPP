# ЗАДАНИЕ 2.5
array = [1, -2, -3, 4, -5, -6, 7, 8, -9, -10, 1, -2, -3]

for i in range(len(array) - 1):
    if array[i] < 0 and array[i+1] < 0:
        print(array[i], array[i+1])

array = list(dict.fromkeys(array))

print(array)