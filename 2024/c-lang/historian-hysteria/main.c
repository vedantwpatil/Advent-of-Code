#include <stdio.h>
#include <stdlib.h>

#define MAX_LINE_LENGTH 1000

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

  int leftList[MAX_LINE_LENGTH];
  int rightList[MAX_LINE_LENGTH];
  int count = 0;

  while (fgets(line, MAX_LINE_LENGTH, pFile)) {
    int first = 0;
    int second = 0;
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
  printf("%d\n", totalDistance);

  fclose(pFile);
  return 0;
}
