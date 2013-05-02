#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <sys/time.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#define PREC_FLOAT	1.e-4
#define tri_ind(i,j) (((i)>(j))?(((i)*((i)+1)>>1)+(j)):(((j)*((j)+1)>>1)+(i)))

typedef	float	flottant;
