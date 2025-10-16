import re

pattern = r"do\(\)|don\'t\(\)|mul\((\d{1,3}),(\d{1,3})\)"

filePath = "input.txt"
totalMatches = 0


def solve(text):
    matches = re.finditer(pattern, text)
    enabled = True
    total = 0

    for match in matches:
        instruction = match.group(0)
        if instruction == "do()":
            enabled = True
        elif instruction == "don't()":
            enabled = False
        elif enabled:  # it's a mul() instruction
            num1, num2 = map(int, match.groups())
            total += num1 * num2

    return total


with open(filePath, "r") as file:
    for line in file:
        totalMatches += solve(line)
    print(totalMatches)
