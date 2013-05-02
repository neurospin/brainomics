#include <stdio.h>
#include <cuda.h>
#include <cuda_runtime.h>
#include <cutil_inline.h>
#include <cutil.h>

#define	BLOCK_SIZEX	1
#define	BLOCK_SIZEY	16
#define	TILE_WIDTH	16

//#define DISPLAY

typedef	float	flottant;

void SaveMat(flottant* beta,size_t width ,size_t height, const char* filename);

int orthoNorm(flottant *x,int siV,int nbV);

void proj(flottant *x,flottant *bp,int siV,int nbX,int nbBp);

void normalize(flottant *x,int siV,int nbX);

void dotProd(const flottant *x,const flottant *y, flottant *beta, int siV,int nbX,int nbY);

void dotProdPerm(const flottant *x,const flottant *y, const int* P, flottant *alpha, int siV,int nbX,int nbY,int nbP);
