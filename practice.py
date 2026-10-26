'''print("LIST")
skills = ["Python", "SQL", "FastAPI", "Git"]
print(skills)
print(skills[0])  # First item
print(skills[-1]) # Last item
skills.append("PostgreSQL")
skills.remove("Git")
print(skills)

print("Dictionaries")

user = {
    "name": "Yash",
    "age": 22,
    "role": "Backend Developer",
    "skills": ["Python", "SQL"]
}
print(user["name"])
print(user["role"])
user["city"] = "Nagpur"
user["age"] = 23
print(user)

Store three subjects and their marks in a dictionary.
Calculate total marks using a function.
Calculate the average marks.
Print the subject with the highest marks.
Display all subjects and marks using a loop.
marks = {
    "Python": 85,
    "SQL": 78,
    "Networking": 92
}'''


def calculate_total(marks):
    total = 0
    for mark in marks.values():
        total += mark
    return total
def calculate_average(marks):
    total = calculate_total(marks)
    average = total / len(marks)
    return average
def find_highest_subject(marks):
    highest_subject = max(marks, key=marks.get)
    return highest_subject
# Student marks
marks = {
    "Python": 85,
    "SQL": 78,
    "Networking": 92
}
# Calculate results
total = calculate_total(marks)
average = calculate_average(marks)
highest_subject = find_highest_subject(marks)
# Display results
print("===== Student Marks Manager =====")
for subject, mark in marks.items():
    print(f"{subject}: {mark}")
print("---------------------------------")
print("Total marks:", total)
print("Average marks:", average)
print("Highest subject:", highest_subject)
print("Highest marks:", marks[highest_subject])
