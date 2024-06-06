class IncorrectTriangleSides(Exception):
    pass

class Triangle:
    # Метод инициализирует объект треугольника и проверяет длины сторон
    def __init__(self, a, b, c):
        if a <= 0 or b <= 0 or c <= 0 or (a + b <= c) or (b + c <= a) or (a + c <= b):
            raise IncorrectTriangleSides("IncorrectTriangleSides (Неправильные стороны треугольника)")
        # Сохраняем длины сторон
        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):
        if self.a == self.b == self.c:
            return "equilateral (равносторонний)"
        elif self.a == self.b or self.a == self.c or self.b == self.c:
            return "isosceles (равнобедренный)"
        else:
            return "nonequilateral (неравносторонний)"

    def perimeter(self):
        return self.a + self.b + self.c


with open("check.txt", "r") as file:
    lines = file.readlines()

    for line in lines:
        triangle = tuple(map(int, line.strip()[1:-1].replace(".", "").split(", ")))
        try:
            t = Triangle(*triangle)
            result = t.triangle_type()
            perimeter = t.perimeter()
            print(f"{triangle}: тип треугольника - {result}, периметр = {perimeter}")
        except IncorrectTriangleSides as e:
            print(f"{triangle}: {str(e)}")