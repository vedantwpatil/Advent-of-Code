package main

import "fmt"

func test() {
	fruits := []string{"apple", "orange", "grape"}

	for index, value := range fruits {
		fmt.Printf("Index: %d, Value: %s\n", index, value)
	}
}
