package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"sort"
	"strconv"
	"strings"
)

func main() {
	filePath := "input.txt"

	file, err := os.Open(filePath)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	var numberLeft []int
	var numberRight []int
	for scanner.Scan() {
		line := scanner.Text()
		fields := strings.Fields(line)
		num1 := fields[0]
		num2 := fields[1]

		num, err := strconv.Atoi(num1)
		if err != nil {
			fmt.Println("Error converting string to integer:", err)
			continue
		}

		numberLeft = append(numberLeft, num)

		num, err = strconv.Atoi(num2)
		if err != nil {
			fmt.Println("Error converting string to integer:", err)
			continue
		}

		numberRight = append(numberRight, num)

		sort.Ints(numberLeft)
		sort.Ints(numberRight)
	}

	var totalDistance float64
	for index := range numberLeft {
		totalDistance += math.Abs(float64(numberLeft[index] - numberRight[index]))
	}
	fmt.Println(int(totalDistance))
}
