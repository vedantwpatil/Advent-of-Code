with open("input.txt", "r") as file:
    count = 0
    totalSum = 50
    for line in file:
        for value in line.split():
            direction = value[0]
            amount = value[1:]
            print(f"Amount: {amount}")

            if direction.lower().__contains__("l"):
                totalSum -= int(amount)
                print("Went to the left: ", totalSum)
            if direction.lower().__contains__("r"):
                totalSum += int(amount)
                print("Went to the right: ", totalSum)

            totalSum = totalSum % 100
            print(f"Adjusted Amount {totalSum}\n")

            if totalSum == 0:
                print("Dial is 0")
                count += 1

    print(count)
