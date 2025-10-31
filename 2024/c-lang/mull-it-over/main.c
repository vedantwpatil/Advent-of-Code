#include "stdio.h"
#include "stdlib.h"
#include <stdio.h>

#define MAX_LINE_LENGTH 1000
int main() {
  printf("Hello World\n");
  FILE *fp = NULL;
  char line[MAX_LINE_LENGTH];

  fp = fopen("input.txt", "r");
  if (fp == NULL) {
    printf("Error opening file");
    return 1;
  }

  fseek(fp, 0L, SEEK_END);
  long size = ftell(fp);
}
