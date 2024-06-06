import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides


class TestGetTriangleType(unittest.TestCase):
    def setUp(self) -> None:  # подготовка прогона теста; вызывается перед каждым тестом
        pass

    def tearDown(self) -> None:  # вызывается после того, как тест был запущен и результат записан.
        # Метод запускается даже в случае исключения (exception) в теле теста
        pass

    def test_equilateral_triangle(self):
        # assert - основной метод тестирования
        self.assertEqual(get_triangle_type(1, 1, 1), "equilateral (равносторонний)")

    def test_isosceles_triangle(self):
        self.assertEqual(get_triangle_type(3, 3, 4), "isosceles (равнобедренный)")

    def test_nonequilateral_triangle(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral (неравносторонний)")

    def test_incorrect_triangle_sides(self):
        self.assertRaises(IncorrectTriangleSides, get_triangle_type, -1, 2, 3)


if __name__ == '__main__':
    unittest.main()
