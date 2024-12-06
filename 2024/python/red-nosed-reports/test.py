filePath = "test.txt"

with open(filePath, "r") as file:
    safeLevels = 0
    for line in file:
        isSafe = True
        levels = line.split()

        for i in range(1, len(levels)):
            first = int(levels[i - 1])
            second = int(levels[i])

            if not 1 <= abs(first - second) <= 3:
                print(f"{first} and {second} is not safe ")
                isSafe = False
                break

        if isSafe:
            safeLevels += 1
    print(safeLevels)
