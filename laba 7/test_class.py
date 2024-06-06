import pytest
from triangle_class import Triangle, IncorrectTriangleSides


def setup_module(module):  # Вызывается перед каждым набором теста
    pass

def teardown_module(module): # Вызывается после каждого набора тестов
    pass

def test_triangle_type_equilateral():
    triangle = Triangle(1, 1, 1)
    assert triangle.triangle_type() == "equilateral (равносторонний)"

def test_triangle_type_isosceles():
    triangle = Triangle(3, 3, 4)
    assert triangle.triangle_type() == "isosceles (равнобедренный)"

def test_triangle_type_nonequilateral():
    triangle = Triangle(3, 4, 5)
    assert triangle.triangle_type() == "nonequilateral (неравносторонний)"

def test_triangle_perimeter():
    triangle = Triangle(3, 4, 5)
    assert triangle.perimeter() == 12

def test_incorrect_triangle_sides():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 0, 0)
        Triangle(1, 1, 3)
        Triangle(-1, 2, 3)

if __name__ == '__main__':
    pytest.main()