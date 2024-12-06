filePath = "input.txt"

with open(filePath, "r") as file:
    listLeft = []
    listRight = []

    for line in file:
        numbers = line.split()

        listLeft.append(numbers[0])
        listRight.append(numbers[1])

    listLeft.sort()
    listRight.sort()
    sumDistance = 0

    similarityScore = 0
    valueFrequency = 0

    setLeft = set(listLeft)
    setRight = set(listRight)

    if listLeft is not None and listRight is not None:
        for i in range(len(listLeft)):
            distance = abs(int(listLeft[i]) - int(listRight[i]))
            sumDistance += distance

        for setNum in setLeft:
            for listNum in listRight:
                if int(setNum) == int(listNum):
                    valueFrequency += 1

            similarityScore += int(setNum) * valueFrequency
            valueFrequency = 0

    print(f"Sum distance is: {sumDistance}")
    print(f"similarity score is: {similarityScore}")
