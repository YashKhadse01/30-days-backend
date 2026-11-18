
'''try:
    age = int(input("Enter your age: "))
    print("Your age is:", age)

except ValueError:
    print("Invalid input! Please enter a number.")

print("Program continues...")


# Write information to a file
with open("student.txt", "w") as file:
    file.write("Name: Yash\n")
    file.write("Course: Backend Development\n")
    file.write("Day: 1\n")

print("Data saved successfully!")

# Read information from the file
with open("student.txt", "r") as file:
    content = file.read()

print(content)'''


try:
    # Get student details
    name = input("Enter student name: ")
    age = int(input("Enter student age: "))
    # Validate age
    if age < 0:
        raise ValueError("Age cannot be negative.")
    # Save details to a file
    with open("student.txt", "w") as file:
        file.write(f"Student Name: {name}\n")
        file.write(f"Student Age: {age}\n")
    print("Student record saved successfully!")
    # Read and display the saved record
    with open("student.txt", "r") as file:
        content = file.read()
    print("\n--- Saved Student Record ---")
    print(content)
except ValueError:
    print("Invalid age! Please enter a valid, non-negative integer.")
except OSError:
    print("File error! Unable to save or read the record.")
