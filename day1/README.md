# Day 01 — Python Fundamentals

**30-Day Python Backend Development Roadmap**

**Date:** 26 October 2026  
**Topic:** Python Core Fundamentals  
**Language:** Python 3.11+  
**Project Type:** Learning Exercises and Small Python Programs

---

## 1. Project Overview

Day 1 focuses on building a strong foundation in Python programming before moving into backend development.

The exercises introduce Python syntax, variables, data types, operators, conditional statements, loops, functions, collections, exception handling, and file operations.

The repository contains introductory examples and practical programs involving student records, marks calculations, user information, and basic numerical operations.

## 2. Learning Objectives

- Understand Python syntax and basic program execution.
- Work with strings, integers, floating-point numbers, and booleans.
- Perform arithmetic calculations.
- Accept user input and convert between data types.
- Use conditional statements and loops.
- Work with lists and dictionaries.
- Write reusable functions.
- Handle invalid inputs using exceptions.
- Read and write text files.
- Organize Python programs into separate files.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| VS Code | Development environment |
| PowerShell | Running Python programs |
| uv | Python project and environment management |
| Git | Version control |
| GitHub | Source-code hosting |

No third-party runtime dependencies are declared in the Day 1 project configuration.

## 4. Project Structure

```text
day1/
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── basics.py
├── practice.py
├── student_record.py
├── user_profil.py
├── student.txt
└── src/
    └── day1/
        └── __init__.py
```

## 5. Python Fundamentals

### Variables and Data Types

Python variables store values without requiring explicit type declarations.

```python
name = "Newton"
age = 22
height = 5.80
is_learning = True

print(type(name))
print(type(age))
print(type(height))
print(type(is_learning))
```

The examples demonstrate the `str`, `int`, `float`, and `bool` data types.

### Arithmetic Operators

Basic arithmetic operations include addition, subtraction, multiplication, and division.

```python
a = 25
b = 15

print(a + b)
print(a - b)
print(a * b)
print(a / b)
```

Division by zero should be checked before performing division.

### Lists

Lists store ordered collections of values.

```python
skills = ["Python", "SQL", "FastAPI", "Git"]

skills.append("PostgreSQL")
skills.remove("Git")
```

The Day 1 examples also demonstrate list indexing.

### Dictionaries

Dictionaries store data as key-value pairs.

```python
user = {
    "name": "Yash",
    "age": 22,
    "role": "Backend Developer",
    "skills": ["Python", "SQL"],
}

print(user["name"])
print(user["role"])
```

Dictionary values can be accessed and updated using their keys.

## 6. Conditional Statements and Loops

The practice exercises cover:

- Checking whether a number is positive, negative, or zero.
- Determining whether a number is odd or even.
- Printing numbers within a specified range.
- Calculating the sum of a numerical sequence.

These concepts are essential for implementing application logic and processing collections of data.

## 7. Functions

Functions help organize logic into reusable units.

### Sum Calculation

```python
def calculate_sum(n):
    total = 0

    for i in range(1, n + 1):
        total += i

    return total
```

### Student Marks Calculation

The marks-management exercise defines three functions:

- `calculate_total(marks)` — Calculates total marks.
- `calculate_average(marks)` — Calculates average marks.
- `find_highest_subject(marks)` — Identifies the subject with the highest marks.

Example dataset:

```python
marks = {
    "Python": 85,
    "SQL": 78,
    "Networking": 92,
}
```

Expected calculations:

```text
Total marks: 255
Average marks: 85.0
Highest subject: Networking
Highest marks: 92
```

## 8. Exception Handling

The exercises introduce `try` and `except` blocks for handling invalid user input.

```python
try:
    age = int(input("Enter your age: "))

    if age < 0:
        raise ValueError("Age cannot be negative.")

except ValueError:
    print("Please enter a valid non-negative integer.")
```

The student-record exercise also demonstrates handling file-related errors using `OSError`.

## 9. File Handling

The project demonstrates reading and writing information using Python's built-in `open()` function.

```python
with open("student.txt", "w") as file:
    file.write("Name: Yash\n")
    file.write("Course: Backend Development\n")
    file.write("Day: 1\n")
```

Reading the file:

```python
with open("student.txt", "r") as file:
    content = file.read()

print(content)
```

The `with` statement ensures the file is closed after the operation.

**Note:** Some file-handling examples overwrite `student.txt`. Back up the file before running exercises that write to it.

## 10. How to Run

### Prerequisites

- Python 3.11 or newer
- VS Code or another code editor
- PowerShell or another terminal

### Navigate to the project

```powershell
cd day1
```

### Run the exercises

```powershell
python basics.py
python practice.py
python student_record.py
python user_profil.py
```

Alternatively, use `uv`:

```powershell
uv run python basics.py
uv run python practice.py
```

Some programs request interactive input. Run each script separately and follow its prompts.

## 11. Practical Applications

The Day 1 concepts form the foundation of backend development.

| Concept | Backend Application |
|---|---|
| Variables | Store application values |
| Dictionaries | Represent structured data |
| Lists | Process collections of records |
| Conditions | Implement business rules |
| Loops | Iterate over datasets |
| Functions | Organize reusable logic |
| Exceptions | Handle invalid inputs |
| File handling | Read and write local data |

## 12. Key Learnings

By completing Day 1, the developer practiced fundamental Python programming concepts and applied them to small exercises.

Important takeaways include understanding program flow, separating calculations into functions, validating user input, and using file operations to store and retrieve information.

## 13. Current Limitations and Future Improvements

- Several exercises are preserved as triple-quoted examples rather than executable code.
- Automated tests are not included in the reviewed Day 1 files.
- Some programs use fixed example values.
- File paths are relative to the working directory.
- Input validation could be expanded.
- Exercises could be separated into smaller modules with dedicated tests.

## 14. Roadmap Progress

**Day 01:** Python Fundamentals

**Next:** Day 02 — Object-Oriented Programming in Python.

---

*Part of the 30-Day Python Backend Development Roadmap.*
