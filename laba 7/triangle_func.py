class IncorrectTriangleSides(Exception):
    pass

def get_triangle_type(a, b, c):
    if a <= 0 or b <= 0 or c <= 0 or (a + b <= c) or (b + c <= a) or (a + c <= b):
        raise IncorrectTriangleSides("IncorrectTriangleSides (Неправильные стороны треугольника)")

    if a == b == c:
        return "equilateral (равносторонний)"
    elif a == b or a == c or b == c:
        return "isosceles (равнобедренный)"
    else:
        return "nonequilateral (неравносторонний)"


with open("check.txt", "r") as file:
    # считываем все строки из файла и сохраняем их в виде списка строк в  lines.
    lines = file.readlines()
    # перебираем каждую строку в lines списке.
    for line in lines:
        # удаляем начальные и конечные пробелы с помощью strip()
        # удаляем круглые скобки с помощью среза [1:-1]
        # удаляет все десятичные точки с помощью replace
        # разбиваем оставшуюся строку на список строк с помощью split(", ").
        triangle = tuple(map(int, line.strip()[1:-1].replace(".", "").split(", ")))
        try:
            # передаем элементы кортежа triangle в качестве отдельных аргументов.
            result = get_triangle_type(*triangle)
            print(f"{triangle}: {result}")
        except IncorrectTriangleSides as e:
            # стороны треугольника и сообщение об ошибке
            print(f"{triangle}: {str(e)}")
