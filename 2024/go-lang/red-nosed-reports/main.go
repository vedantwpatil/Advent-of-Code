package main

import (
	"bufio"
	"fmt"
	"log"
	"math"
	"os"
	"strconv"
	"strings"
)

func errorLogging(errorType error) {
	if errorType != nil {
		log.Fatalf("Error: %s", errorType)
	}
}

func isIncreasing(arr []int) bool {
	for i := 0; i < len(arr)-1; i++ {
		if arr[i] >= arr[i+1] {
			return false
		}
	}
	return true
}

func isDecreasing(arr []int) bool {
	for i := 0; i < len(arr)-1; i++ {
		if arr[i] <= arr[i+1] {
			return false
		}
	}
	return true
}

func checkSafe(arr []int) bool {
	for i := 1; i < len(arr); i++ {
		diff := math.Abs(float64(arr[i] - arr[i-1]))
		if diff < 1 || diff > 3 {
			return false
		}
	}
	return true
}

func convertIntoInt(fields []string) []int {
	var returnSlice []int

	for _, value := range fields {
		parsedValue, err := strconv.Atoi(value)
		errorLogging(err)
		returnSlice = append(returnSlice, parsedValue)
	}

	return returnSlice
}

func main() {
	file, err := os.Open("input.txt")
	errorLogging(err)

	defer file.Close()
	totalSafeCount := 0

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		words := strings.Fields(line)

		nums := convertIntoInt(words)

		if (isIncreasing(nums) || isDecreasing(nums)) && checkSafe(nums) {
			totalSafeCount++
		}
	}

	fmt.Println("Total safe count:", totalSafeCount)
}
