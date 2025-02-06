#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LENGTH 1000

typedef struct {
  int left;
  int right;
} Pair;

int pair_comparator(const void *a, const void *b) {
  Pair *pa = (Pair *)a;
  Pair *pb = (Pair *)b;

  return (pa->left - pb->left) | (pa->right - pb->right);
}

int compare_ints(const void *a, const void *b) {
  return (*(int *)a - *(int *)b);
}

int main() {
  FILE *pFile = NULL;
  char line[MAX_LINE_LENGTH];

  pFile = fopen("input.txt", "r");

  if (pFile == NULL) {
    printf("Error opening the file");
    return 1;
  }

  fseek(pFile, 0L, SEEK_END);
  long size = ftell(pFile);

  printf("File size: %ld bytes\n", size);
  fseek(pFile, 0L, 0);

  // Added 1 for the null terminator
  char *buffer = malloc(size + 1);

  // Implement dynamic resizing
  int *leftList = malloc(sizeof(int) * size);
  int *rightList = malloc(sizeof(int) * size);

  if (leftList == NULL || rightList == NULL) {
    printf("Issue allocating memory");
    return 1;
  }

  size_t capacity = size;
  int count = 0;

  while (fgets(line, MAX_LINE_LENGTH, pFile)) {
    int first = 0;
    int second = 0;
    if (count >= capacity) {
      leftList = realloc(leftList, capacity * sizeof(int));
      rightList = realloc(rightList, capacity * sizeof(int));
    }
    if (sscanf(line, "%d%*[^0-9]%d", &first, &second) != 2) {
      printf("Error reading numbers\n");
      continue;
    }

    leftList[count] = first;
    rightList[count] = second;
    count++;
  }

  qsort(leftList, count, sizeof(int), compare_ints);
  qsort(rightList, count, sizeof(int), compare_ints);

  int totalDistance = 0;
  for (int i = 0; i < MAX_LINE_LENGTH; i++) {
    int distance = abs(leftList[i] - rightList[i]);
    totalDistance += distance;
  }

  printf("Total Distance: %d\n", totalDistance);

  free(buffer);

  free(leftList);
  free(rightList);

  fclose(pFile);
  return 0;
}
