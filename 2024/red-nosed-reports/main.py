def isIncreasing(arr):
    return all(i < j for i, j in zip(arr, arr[1:]))


def isDecreasing(arr):
    return all(i > j for i, j in zip(arr, arr[1:]))


def checkSafe(arr):
    for i in range(1, len(arr)):
        if not 1 <= abs(arr[i] - arr[i - 1]) <= 3:
            return False
    return True


def removeOneBadElementAndCheck(arr):
    for i in range(len(arr)):
        # Create new array without element at index i
        temp_arr = arr[:i] + arr[i + 1 :]
        if (isIncreasing(temp_arr) or isDecreasing(temp_arr)) and checkSafe(temp_arr):
            return True
    return False


try:
    with open("input.txt", "r") as file:
        safeLevels = 0
        for line in file:
            # Convert every element into a int
            levels = [int(x) for x in line.split()]

            # First check if safe without removing elements
            if (isIncreasing(levels) or isDecreasing(levels)) and checkSafe(levels):
                safeLevels += 1
                continue

            # If not safe, try removing one element
            if removeOneBadElementAndCheck(levels):
                safeLevels += 1

        print("Total safe reports:", safeLevels)
except FileNotFoundError:
    print("Input file not found")
