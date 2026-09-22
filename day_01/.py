"""
Day 1 Practice: Variables, Data Types and Input/Output

Practice programs:
1. Variables and basic data types
2. Sum of two numbers
3. Average marks
4. Temperature conversion
5. Area and perimeter
6. Swap two values
7. Extract digits from a number
8. Simple interest
9. Convert seconds to hours, minutes and seconds
10. Student information
11. Type conversion
12. Constants and formatted output

Python 3.x
"""


def program_1_variables_and_data_types():
    print("\n--- Program 1: Variables and Data Types ---")

    student_name = "Atul"
    age = 25
    percentage = 87.5
    grade = "A"
    passed = True

    print("Student Name:", student_name)
    print("Age:", age)
    print("Percentage:", percentage)
    print("Grade:", grade)
    print("Passed:", passed)

    print("\nData types:")
    print("student_name:", type(student_name))
    print("age:", type(age))
    print("percentage:", type(percentage))
    print("grade:", type(grade))
    print("passed:", type(passed))


def program_2_sum_of_two_numbers():
    print("\n--- Program 2: Sum of Two Numbers ---")

    first_number = float(input("Enter the first number: "))
    second_number = float(input("Enter the second number: "))

    total = first_number + second_number

    print("First number :", first_number)
    print("Second number:", second_number)
    print("Sum          :", total)


def program_3_average_marks():
    print("\n--- Program 3: Average Marks ---")

    number_of_subjects = int(input("Enter number of subjects: "))

    if number_of_subjects <= 0:
        print("Number of subjects must be greater than zero.")
        return

    total_marks = 0.0

    for subject_number in range(1, number_of_subjects + 1):
        marks = float(input(f"Enter marks for subject {subject_number}: "))
        total_marks += marks

    average = total_marks / number_of_subjects

    print("\nTotal marks:", total_marks)
    print("Average    :", average)


def program_4_temperature_conversion():
    print("\n--- Program 4: Temperature Conversion ---")
    print("1. Celsius to Fahrenheit")
    print("2. Fahrenheit to Celsius")

    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        celsius = float(input("Enter temperature in Celsius: "))
        fahrenheit = (celsius * 9 / 5) + 32
        print(f"{celsius} °C = {fahrenheit:.2f} °F")

    elif choice == "2":
        fahrenheit = float(input("Enter temperature in Fahrenheit: "))
        celsius = (fahrenheit - 32) * 5 / 9
        print(f"{fahrenheit} °F = {celsius:.2f} °C")

    else:
        print("Invalid choice.")


def program_5_area_and_perimeter():
    print("\n--- Program 5: Area and Perimeter ---")
    print("1. Rectangle")
    print("2. Square")
    print("3. Circle")

    choice = input("Choose a shape (1/2/3): ")

    if choice == "1":
        length = float(input("Enter length: "))
        width = float(input("Enter width: "))

        if length <= 0 or width <= 0:
            print("Length and width must be positive.")
            return

        print("Area     :", length * width)
        print("Perimeter:", 2 * (length + width))

    elif choice == "2":
        side = float(input("Enter side length: "))

        if side <= 0:
            print("Side length must be positive.")
            return

        print("Area     :", side ** 2)
        print("Perimeter:", 4 * side)

    elif choice == "3":
        radius = float(input("Enter radius: "))

        if radius <= 0:
            print("Radius must be positive.")
            return

        pi = 3.141592653589793
        print("Area         :", pi * radius ** 2)
        print("Circumference:", 2 * pi * radius)

    else:
        print("Invalid choice.")


def program_6_swap_two_values():
    print("\n--- Program 6: Swap Two Values ---")

    first_value = input("Enter the first value: ")
    second_value = input("Enter the second value: ")

    print("\nBefore swapping:")
    print("First value :", first_value)
    print("Second value:", second_value)

    first_value, second_value = second_value, first_value

    print("\nAfter swapping:")
    print("First value :", first_value)
    print("Second value:", second_value)


def program_7_extract_digits():
    print("\n--- Program 7: Extract Digits ---")

    number = int(input("Enter an integer: "))
    original_number = number
    number = abs(number)

    if number == 0:
        print("Digit: 0")
        return

    digits = []

    while number > 0:
        digit = number % 10
        digits.append(digit)
        number //= 10

    print("Original number:", original_number)
    print("Digits from right to left:", digits)
    print("Digits from left to right :", digits[::-1])
    print("Number of digits:", len(digits))


def program_8_simple_interest():
    print("\n--- Program 8: Simple Interest ---")

    principal = float(input("Enter principal amount: "))
    rate = float(input("Enter annual interest rate (%): "))
    time = float(input("Enter time in years: "))

    if principal < 0 or rate < 0 or time < 0:
        print("Values cannot be negative.")
        return

    simple_interest = (principal * rate * time) / 100
    total_amount = principal + simple_interest

    print("\nPrincipal amount :", principal)
    print("Interest rate    :", rate, "%")
    print("Time             :", time, "years")
    print("Simple interest  :", simple_interest)
    print("Total amount     :", total_amount)


def program_9_convert_seconds():
    print("\n--- Program 9: Seconds Conversion ---")

    total_seconds = int(input("Enter total seconds: "))

    if total_seconds < 0:
        print("Seconds cannot be negative.")
        return

    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    print("\nTotal seconds:", total_seconds)
    print("Hours        :", hours)
    print("Minutes      :", minutes)
    print("Seconds      :", seconds)
    print(f"Formatted time: {hours:02d}:{minutes:02d}:{seconds:02d}")


def program_10_student_information():
    print("\n--- Program 10: Student Information ---")

    name = input("Enter student name: ")
    age = int(input("Enter age: "))
    course = input("Enter course name: ")

    print("\nEnter marks for three subjects.")
    subject_1 = float(input("Subject 1 marks: "))
    subject_2 = float(input("Subject 2 marks: "))
    subject_3 = float(input("Subject 3 marks: "))

    total = subject_1 + subject_2 + subject_3
    average = total / 3

    passed = (
        subject_1 >= 40
        and subject_2 >= 40
        and subject_3 >= 40
    )

    print("\n========== STUDENT REPORT ==========")
    print("Name    :", name)
    print("Age     :", age)
    print("Course  :", course)
    print("Total   :", total)
    print("Average :", round(average, 2))
    print("Passed  :", passed)
    print("====================================")


def program_11_type_conversion():
    print("\n--- Program 11: Type Conversion ---")

    integer_text = input("Enter an integer: ")
    decimal_text = input("Enter a decimal number: ")

    integer_value = int(integer_text)
    decimal_value = float(decimal_text)

    print("\nOriginal values are strings:")
    print("integer_text:", integer_text)
    print("decimal_text:", decimal_text)

    print("\nConverted values:")
    print("integer_value:", integer_value)
    print("decimal_value:", decimal_value)

    print("\nTypes:")
    print("integer_value:", type(integer_value))
    print("decimal_value:", type(decimal_value))

    print("\nExample calculations:")
    print("Integer + 10:", integer_value + 10)
    print("Decimal * 2  :", decimal_value * 2)


def program_12_constants_and_output():
    print("\n--- Program 12: Constants and Formatted Output ---")

    # Python uses uppercase naming by convention for constants.
    PI = 3.141592653589793
    GST_RATE = 0.18

    price = float(input("Enter product price: "))

    gst = price * GST_RATE
    final_price = price + gst

    print("\n========== BILL ==========")
    print(f"Product price : ₹{price:.2f}")
    print(f"GST (18%)     : ₹{gst:.2f}")
    print(f"Final price   : ₹{final_price:.2f}")
    print("==========================")
    print("PI value:", PI)


def show_menu():
    print("\n" + "=" * 60)
    print("DAY 1 PYTHON PRACTICE")
    print("Variables, Data Types and Input/Output")
    print("=" * 60)
    print("1. Variables and data types")
    print("2. Sum of two numbers")
    print("3. Average marks")
    print("4. Temperature conversion")
    print("5. Area and perimeter")
    print("6. Swap two values")
    print("7. Extract digits")
    print("8. Simple interest")
    print("9. Convert seconds")
    print("10. Student information")
    print("11. Type conversion")
    print("12. Constants and formatted output")
    print("0. Exit")
    print("=" * 60)


def main():
    programs = {
        "1": program_1_variables_and_data_types,
        "2": program_2_sum_of_two_numbers,
        "3": program_3_average_marks,
        "4": program_4_temperature_conversion,
        "5": program_5_area_and_perimeter,
        "6": program_6_swap_two_values,
        "7": program_7_extract_digits,
        "8": program_8_simple_interest,
        "9": program_9_convert_seconds,
        "10": program_10_student_information,
        "11": program_11_type_conversion,
        "12": program_12_constants_and_output,
    }

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("\nPractice session completed.")
            break

        selected_program = programs.get(choice)

        if selected_program is None:
            print("\nInvalid choice. Please select a number from 0 to 12.")
            continue

        selected_program()
        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()
