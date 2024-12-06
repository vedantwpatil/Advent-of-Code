filePath = "input.txt"

with open(filePath, "r") as file:
    for line in file:
        words = []
        for letter in line:
            words.append(letter)
            
            if words.
