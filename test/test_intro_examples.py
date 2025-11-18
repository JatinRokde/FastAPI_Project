import pytest


def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1


def test_is_instance():
    assert isinstance('a string', str)
    assert isinstance('10', str)


def test_boolean():
    validated = True
    assert validated is True
    validated = False
    assert validated is False


def test_type():
    assert type('Hello' is str)
    assert type('World' is not int)


def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10


def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)


class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: str):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def student():
    return Student('Test', 'User', 'Mathematics', '1990')


def test_person_initialization(student):
    s = Student('Test', 'User', 'Mathematics', '1990')
    assert student.first_name == 'Test'
    assert student.last_name == 'User'
    assert student.major == 'Mathematics'
    assert student.years == '1990'
