with open("input.txt", "r") as file:
    text = file.read()
    sum = 0

    lines = text.split("\n")

    for line in lines:
        digits = []

        for char in line:
            if char.isdigit():
                digits.append(char)

        if digits:
            first_digit = digits[0]
            last_digit = digits[-1]
            number = first_digit + last_digit

            sum += int(number)

    print(f"The total of the calibration values is {sum}")
