#Understanding yield
#A normal function uses return to finish and give back a result.
#A generator uses yield to produce a value and pause execution. When requested again, it resumes from where it stopped.

def count_numbers():
    print("Starting generator")
    yield 1
    yield 2
    yield 3
numbers = count_numbers()
print(next(numbers))
print(next(numbers))
print(next(numbers))

#A practical generator using a loop
def generate_numbers(limit):
    for number in range(1, limit + 1):
        yield number
for value in generate_numbers(5):
    print(value)

#Write a generator called even_numbers(limit) that produces only even numbers from 1 to limit
# Step 1: Create a generator
def even_numbers(limit):
    for number in range(1, limit + 1):
        if number % 2 == 0:
            yield number
# Step 2: Call the generator
print("Even numbers from 1 to 10:")
for number in even_numbers(10):
    print(number)
print("\nUsing next():")
numbers = even_numbers(10)
print(next(numbers))  # 2
print(next(numbers))  # 4
print(next(numbers))  # 6