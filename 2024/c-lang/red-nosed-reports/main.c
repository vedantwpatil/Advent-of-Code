#include "stdlib.h"
#include <stdio.h>

#define MAX_LINE_LENGTH 10000

int main(int argc, char *argv[]) {
  char *filePath = "input.txt";
  FILE *pFile = fopen(filePath, "r");

  if (pFile == NULL) {
    printf("Issue opening file");
  }

  char line[MAX_LINE_LENGTH];
  while (fgets(line, MAX_LINE_LENGTH, pFile)) {
  }
  return 0;
}
