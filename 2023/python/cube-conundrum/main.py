import math

file_path = "input.txt"
with open(file_path, "r") as file:
    text = file.read()

    lines = text.strip().split("\n")
    sumTotalPossibleGameNumbers = 0
    sumSetPower = 0

    for line in lines:
        parts = line.split(": ")
        gameNumber = int(parts[0].split()[1])
        gamesPlayed = parts[1].split("; ")

        possible = True

        for game in gamesPlayed:
            red = green = blue = 0

            gameList = game.split(", ")

            for element in gameList:
                count, color = element.split()
                count = int(count)
                if color == "red":
                    red = count
                elif color == "green":
                    green = count
                elif color == "blue":
                    blue = count

            if red > 12 or green > 13 or blue > 14:
                possible = False

            if len(gameList) == 3 and possible:
                minRed = minGreen = minBlue = 14
                setPower = 0

                if red > 1 and green > 1 and blue > 1:
                    minRed = min(minRed, red)
                    minBlue = min(minBlue, blue)
                    minGreen = min(minGreen, green)

                    setPower = minRed * minGreen * minBlue
                    sumSetPower += setPower

        if possible:
            sumTotalPossibleGameNumbers += gameNumber

    print(sumTotalPossibleGameNumbers)
    print(sumSetPower)
