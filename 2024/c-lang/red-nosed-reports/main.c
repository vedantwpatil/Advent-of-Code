#include "stdbool.h"
#include "stdlib.h"
#include <stdio.h>
#include <string.h>

bool is_valid_sequence(const char *line) {
  int capacity = 10;
  int *numbers = malloc(capacity * sizeof(int));

  if (numbers == NULL) {
    printf("Error allocating memory");
    exit(EXIT_FAILURE);
  }

  // Convert the characters into integers
  int count = 0;
  char *token = strtok((char *)line, " \n");

  // Parse all numbers from the line
  while (token != NULL) {

    // Resizing
    if (count >= capacity) {

      capacity *= 2;
      int *temp = realloc(numbers, capacity * sizeof(int));

      if (temp == NULL) {
        printf("Error reallocating");
        free(numbers);
        return false;
      }
      numbers = temp;
    }

    numbers[count++] = atoi(token);
    token = strtok(NULL, " \n");
  }

  if (count < 2) {
    free(numbers);
    return false;
  }

  bool increasing = true;
  bool decreasing = true;

  // Check the sequence
  for (int i = 1; i < count; i++) {
    int difference = numbers[i] - numbers[i - 1];

    // Check if difference is within valid range (1-3)
    if (abs(difference) > 3 || difference == 0) {
      free(numbers);
      return false;
    }

    // Check if sequence breaks increasing/decreasing pattern
    if (difference > 0) {
      decreasing = false;
    } else {
      increasing = false;
    }

    // If neither increasing nor decreasing, sequence is invalid
    if (!increasing && !decreasing) {
      free(numbers);
      return false;
    }
  }

  free(numbers);
  return true;
}

int main(int argc, char *argv[]) {
  char *filePath = "input.txt";
  FILE *pFile = fopen(filePath, "r");

  if (pFile == NULL) {
    printf("Issue opening file");
    return EXIT_FAILURE;
  }

  fseek(pFile, 0L, SEEK_END);
  long size = ftell(pFile) + 1;
  fseek(pFile, 0L, 0);

  char *line = malloc(size);

  if (line == NULL) {
    printf("Issue allocating memory");
    return EXIT_FAILURE;
  }

  int amt_safe_lines = 0;
  while (fgets(line, size, pFile)) {
    while (strchr(line, '\n') == NULL) {
      size *= 2;
      line = realloc(line, size);

      if (line == NULL) {
        printf("Issue reallocating memory");
        return EXIT_FAILURE;
      }

      fgets(line + strlen(line), size - strlen(line), pFile);
    }

    if (is_valid_sequence(line)) {
      amt_safe_lines++;
    }
  }

  printf("File size: %ld bytes\n", size);
  printf("Amount of safe reports: %d\n", amt_safe_lines);

  free(line);
  fclose(pFile);
  return EXIT_SUCCESS;
}
