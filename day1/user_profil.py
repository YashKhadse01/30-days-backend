'''- Takes a user's name, age, and monthly salary as input.
- Prints a welcome message using an f-string.
- Calculates their annual salary.
- Prints their age after five years.
- Displays the data type of each variable.'''

'''name=input("Enter a name:- ")
age=int(input("Enter age:- "))
monthly_salary=float(input("Enter salary:- "))

print(f"welcome to my roadmap {name}")
annual_salary=monthly_salary * 12
print(annual_salary)

print(f"Age after five years is {age + 5}")

print(type(name))
print(type(age))
print(type(monthly_salary))
print(type(annual_salary))'''

'''Write a program that asks the user for a number and:
1. Prints whether the number is positive, negative, or zero.
2. Prints whether it's even or odd.
3. Prints all numbers from 1 to that number using a for loop.
4. Calculates the sum of all numbers from 1 to that number.'''

'''num=int(input("Enter a number:- "))
if num > 0:
    print("positive")
elif num < 0:
    print("Negative")
elif num == 0:
    print("Zero")

if num%2:
    print("odd")
else:
    print("Even")
for i in range(1,num+1):
    print(i)
s=0
for i in range(1,num+1):
    s=s+i
print("Sum up to entered number",s)'''


def calculate_sum(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total
num = int(input("Enter a positive number: "))
result = calculate_sum(num)
print("Sum:", result)


