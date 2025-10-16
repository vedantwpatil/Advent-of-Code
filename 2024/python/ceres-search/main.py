filePath = "input.txt"

with open(filePath, "r") as file:
    text = file.read()
    for row in range(len(text)):
        for col in range(len(text[row])):
            up = text[row - 1][col]
            down = text[row + 1][col]
            right = text[row][col + 1]
            left = text[row][col - 1]

            topRight = text[row - 1][col + 1]
            topLeft = text[row - 1][col - 1]
            bottomRight = text[row + 1][col + 1]
            bottomLeft = text[row + 1][col - 1]

