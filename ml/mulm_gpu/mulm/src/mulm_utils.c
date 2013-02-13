#include "mulm_utils.h"

/**SaveMat saves a matrix in a text file (used for beta and mean_scores if DISPLAY is defined in linear_model.h)
**/
void SaveMat(flottant* beta,size_t width ,size_t height, const char* filename)
{
	FILE *filePtr;
	filePtr = fopen(filename,"w");
	int i,j;
	for (j = 0; j<height; j++){
		for (i = 0; i < width; i++){
			fprintf(filePtr, "%f ", beta[j*width + i]);
	   	}
	   	fprintf(filePtr, "\n");
	}
}

/**orthoNorm orthonormalizes the matrix on axis 0)
**/
int orthoNorm(flottant *x,int siV,int nbV)
{
	int i, j, k;
	int lost_dof=0;
	printf("Fonction OrthoNorm()\n");
	flottant nrm = 0;
	/* le principe est de calculer l'ensemble des produit scalaire x_i.x_j puis de faire touver l'orthonormalisation par calcul d'une matrice de transformation et d'un update des produit scalaire , les matrice etant symetrique on ne stocke que les triangles*/
	flottant *mat=(flottant*)calloc(((nbV*(nbV+1))>>1),sizeof(flottant)); /*nombre de valeur dans le triangle =(n*n+1)/2*/
	flottant *trans=(flottant*)calloc(((nbV*(nbV+1))>>1),sizeof(flottant));
	for(i=0; i<nbV; i++)
	trans[((i*(i+1))>>1)+i]=1;

	/*calcul de tt les produits scalaires*/
	for(i=0;i<nbV;i++)
	  for(j=0;j<=i;j++)
	    for(k=0;k<siV;k++)
		mat[((i*(i+1))>>1)+j]+=x[k+siV*i]*x[k+siV*j];

	/*udate des produit scalaire et de la mat de transformation*/
	for(i=0;i<nbV;i++)
	{
		if(mat[((i*(i+1))>>1)+i]>PREC_FLOAT)
			nrm=1/sqrt(mat[((i*(i+1))>>1)+i]);
		else
			nrm=0;	 

		for(j=0;j<nbV;j++)
		{
			mat[tri_ind(i,j)]*=nrm;
			trans[tri_ind(i,j)]*=nrm;
		}
		mat[((i*(i+1))>>1)+i]=(nrm!=0.?1.:0);

		for(j=i+1;j<nbV;j++)
		{
			flottant tmp=mat[tri_ind(i,j)];
			trans[tri_ind(i,j)]-=tmp;

			for(k=nbV-1;k>=0;k--)
				mat[tri_ind(k,j)]-=tmp*mat[tri_ind(i,k)];
		}
	}
	/*mise a jour du vecteur*/
	for(i=0;i<nbV;i++)
	{
		for(k=0;k<siV;k++)
			x[i*siV+k]*=trans[tri_ind(i,i)];

		for(j=0;j<i;j++)
		      for(k=0;k<siV;k++)
			x[i*siV+k]+=trans[tri_ind(i,j)]*x[j*siV+k];
	}

	free(mat);
	free(trans);
	return lost_dof;  
}

/**Project matrix x on orthonormal matrix bp
**/
void proj(flottant *x,flottant *bp,int siV,int nbX,int nbBp)
{
	int i, j, k;
	printf("Fonction Projection()\n");
	for(i=0;i<nbX;i++)
	{
	    for(j=0;j<nbBp;j++)
	    {
		  flottant dot=0;
		  for(k=0;k<siV;k++)
		    dot+=x[i*siV+k]*bp[j*siV+k];
		  for(k=0;k<siV;k++)
		    x[i*siV+k]-=bp[j*siV+k]*dot;
	    }
	}
}

/**normalize a matrix
**/
void normalize(flottant *x,int siV,int nbX)
{
  int i, j;
  flottant nrm=0;
  printf("Fonction Normalize\n");
   for(j=0;j<nbX;j++)
   {
	  nrm=0;
	  for(i=0;i<siV;i++)
	    nrm+=x[siV*j+i]*x[siV*j+i];
	  nrm=sqrt(nrm);
	  for(i=0;i<siV;i++)
	    x[siV*j+i]/=nrm;
   }
}

/**Calculates the dot product for each permutation (used to calculate alpha)
**/
void dotProdPerm(const flottant *x,const flottant *y, const int* P, flottant *alpha, int siV,int nbX,int nbY,int nbP)
{
  int i, j, k, p;
  flottant dot=0;
  int ind;
  printf("Fonction dotProdPerm\n");
  for(p=0; p<nbP; p++){
     for(k=0;k<nbX;k++){
	for(j=0;j<nbY;j++){
	  dot=0;
	  for(i=0;i<siV;i++){
	    ind = P[p*siV+i];
	    dot+=x[k*siV+ind]*y[j*siV+i];
	  }
	  alpha[k*nbP + p]+=dot*dot;
	}
    }
  }
}

