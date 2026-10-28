#mypy is a static type checker for Python. It analyzes your type annotations and helps detect mistakes before you run your program.
def calculate_salary(
    basic_salary: int,
    bonus: int
) -> int:
    return basic_salary + bonus
salary = calculate_salary(30000, 5000)
print("Total salary:", salary)
