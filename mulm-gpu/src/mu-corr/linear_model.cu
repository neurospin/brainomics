#include "linear_model.h"
/**
   kernel : computation of Y.X and the score for p permutations
   Selection of the scores over the threshold.
**/
// Macro definition
#define CudaAssert( X )  if ( !(X) ) { return; }

#define	BLOCK_SIZEX	1

#define	BLOCK_SIZEY 32
#define bsize 128
#define nb_permut_per_th 8

int get_block_sizey() { return BLOCK_SIZEY; }
int get_bsize() { return bsize; }
int get_nb_permut_per_th() { return nb_permut_per_th; }

/**
 * Cuda kernel for d_X.d_y dot product and F scores with permutations
 * and covariates bias correction, plus thresholding for sparse COO
 * array output.
 **/
__global__ void Kernel_DotProd(const flottant* d_X,
			       const flottant* d_Y,
			       const int* d_P,
			       flottant *d_out,
			       const flottant *dalpha,
			       const size_t VectorSize,
			       const int num_vector_Y,
			       const int num_permut,
			       unsigned int *cmpt,
			       const int dof,
			       const double threshold,
			       const int max_size,
			       unsigned int *flag
			       )
{
  extern __shared__ flottant shared[];
  flottant *X = &shared[0];
  flottant A;
  int tid= threadIdx.z+threadIdx.y*blockDim.z;
  __shared__ double dot[nb_permut_per_th*bsize];
  int y_id = blockIdx.y*blockDim.y + threadIdx.y;
  int z_id = blockIdx.z*blockDim.z + threadIdx.z;
  unsigned int ind,k;
  
  // initialize dot[] to 0
  for(int j=0;j<nb_permut_per_th;j++)
    dot[j*bsize+tid]=0;

  // the block of threads loads X
  for(k=0; k<VectorSize; k+=blockDim.z*blockDim.y)
    if((k+threadIdx.y+threadIdx.z*blockDim.y)<VectorSize)
      X[k+threadIdx.y+threadIdx.z*blockDim.y]=d_X[blockIdx.x*VectorSize+k+threadIdx.y+threadIdx.z*blockDim.y];

  __syncthreads(); // wait until data are loaded
  
  // dot(X[perm],Y), ie. beta computation
  for(k=0;k<VectorSize;k++)
    {
      A=d_Y[num_vector_Y*(k)+y_id];
      for(int j=0;j<nb_permut_per_th;j++)
	{
	  ind=d_P[(nb_permut_per_th*z_id+j)*VectorSize+k];
	  dot[j*bsize+tid]+= X[ind]*A;
	}
    }

  // F score and filter
  for(int j=0;j<nb_permut_per_th;j++)
    {
      // load a^2 for covariates bias correction
      A=dalpha[y_id+num_vector_Y*(nb_permut_per_th*z_id+j)];
      /* compute F score*/
      dot[bsize*j+tid]*=dot[bsize*j+tid]; // b^2
      A+=dot[bsize*j+tid]; // a^2 + b^2 
      dot[bsize*j+tid] *= dof; // b^2 * dof
      dot[bsize*j+tid]/=(1.-A); // (b^2 * dof) / (1 - (a^2 + b^2))
      
      if(dot[bsize*j+tid] > threshold )
	{
	  // reach max allocated size?
	  CudaAssert( ( *cmpt < max_size ) );
	  // atomic incrementation to write next element in d_out
	  ind = atomicInc(cmpt, max_size);
	  // set a flag if max_size was reached
	  (*flag)|=(ind > max_size - 1) ;
	  if(ind<max_size)
	    {
	      d_out[4 * ind] = dot[bsize*j+tid];
	      d_out[4 * ind + 1] = blockIdx.x;
	      d_out[4 * ind +2] = y_id;
	      d_out[4 * ind +3] = nb_permut_per_th*z_id+j;
	    }
	}
    }
}

/**
 * Management of Cuda host code and kernel Launch
 *
 * 1 - Set CUDA environment, device, etc 
 * 2 - Set block and grid size
 * 3 - Allocate, initialize and copy memory to device 
 * 4 - Launch kernel
 **/
int  dotProdDevice(const flottant *x_in, 
		   const flottant *y_in,
		   flottant *beta, 
		   flottant *alpha,
		   int *p_python,
		   size_t VectorSize, int nSubj, 
		   int num_vector_X,
		   int num_vector_Y,
		   int num_vector_Z,
		   int num_permut,
		   flottant divide,
		   double threshold,
		   int dev
		   )
{
  flottant *dx_in;
  flottant *dy_in;
  flottant *dalpha;
  int *dp_in;
  flottant *d_out;
  unsigned int *cmpt;
  unsigned int *flag;
  unsigned int hcmpt;
  unsigned int hflag;
  unsigned int total_cmpt = 0;
  size_t YSize = num_vector_Y * VectorSize * sizeof(flottant);
  size_t XSize = num_vector_X * VectorSize * sizeof(flottant);
  size_t PSize = num_permut * VectorSize * sizeof(int);
  size_t ASize = num_vector_Y * num_permut * sizeof(flottant);
  size_t TotalSize = num_vector_X * num_vector_Y * divide * sizeof(flottant);
  size_t SubTotalMem;

  //////////////// Get Properties of the device and parametrize tiling ////////////////
  int deviceNb;
  cudaGetDeviceCount(&deviceNb);
  cudaSetDeviceFlags(cudaDeviceScheduleYield);
  if(dev<deviceNb) {
    cudaSetDevice(dev);
  } else {
    fprintf(stderr, "# %d is not a valid device Id\n", dev);
    exit(-1);
  }
  cudaDeviceProp deviceProp;
  cudaGetDeviceProperties(&deviceProp, dev);
  size_t free_device_mem, total_device_mem;
  cudaMemGetInfo(&free_device_mem, &total_device_mem);
  size_t globalLeft = free_device_mem * 4 / 5;
  if(globalLeft < (XSize + YSize + PSize + ASize)) {
    fprintf(stderr, "# Cannot allocate input data on device. Max Memory exceeded : %lu MB / %lu MB \n",
	    (XSize + YSize + PSize + ASize) / 1048576, globalLeft / 1048576);
    exit(0);
  } else 
    globalLeft -= (XSize + YSize + PSize + ASize);
 	
  int BlockSizeY = BLOCK_SIZEY;
  int BlockSizeP = bsize / BLOCK_SIZEY;
  int BlockSizeX = BLOCK_SIZEX;
	
  int maxGridSize0 = deviceProp.maxGridSize[0];
  int maxGridSize1 = deviceProp.maxGridSize[1];
  int maxGridSize2 = deviceProp.maxGridSize[2];

  int nb_block_x = num_vector_X;
  int nb_block_y = num_vector_Y / BlockSizeY;
  int nb_block_p = num_permut / BlockSizeP;

  if(nb_block_x > maxGridSize0) {
    fprintf(stderr, "# Exceeding Max X Grid Size \n");
    nb_block_x = nb_block_x / (nb_block_x / maxGridSize0 + 1) + 1;
  }
  if(nb_block_y > maxGridSize1) {
    fprintf(stderr, "# Exceeding Max Y Grid Size \n");
    nb_block_y = nb_block_y / (nb_block_y / maxGridSize1 + 1) + 1;
  }
  if(nb_block_p > maxGridSize2) {
    fprintf(stderr, "# Error : Exceeding Max Z Grid Size \nCannot have num_permut bigger than %d\n",maxGridSize2);
    exit(0); 
  }

   size_t size = nb_block_x * BlockSizeX * nb_block_y * BlockSizeY * divide * sizeof(flottant);

  if(size > globalLeft) {
    fprintf(stderr, "# Exceeding GPU Memory Capacity \n");
    nb_block_y = nb_block_y / (size / globalLeft + 1) + 1;
    fprintf(stderr, "# Number of GPU iterations needed =  %lu\n", size / globalLeft + 1);
  }

  int XVectPerCall = nb_block_x * BlockSizeX;
  int YVectPerCall = nb_block_y * BlockSizeY;

  dim3 dimBlock(BlockSizeX, BlockSizeY, BlockSizeP);
  dim3 dimGrid(nb_block_x, nb_block_y, nb_block_p / nb_permut_per_th);

  SubTotalMem = XVectPerCall * YVectPerCall * divide * nb_permut_per_th * sizeof(flottant);
  fprintf(stderr, "# d_out memory allocated = %lu\n", SubTotalMem);

  size_t max_size = XVectPerCall * YVectPerCall * divide * nb_permut_per_th / 4;
  fprintf(stderr,"# Maximum number of values allowed per iteration = %G\n", (double)max_size);
  size_t sharedMem = ((VectorSize / 32) * 32) * sizeof(flottant);
  fprintf(stderr,"# SharedMem = %G\n", (double)sharedMem);		

  ///////////////// Allocation and Copy of input data ////////////////

  // allocate memory for arrays in the device
  cudaMalloc( &dx_in, XSize);
  cudaMalloc( &dy_in, YSize);
  cudaMalloc( &dalpha, ASize);
  cudaMalloc( &dp_in, PSize);
  cudaMalloc( &cmpt, sizeof(int));
  cudaMalloc( &flag, sizeof(int));
	
  //copy data from host to device
  cudaMemcpyAsync(dx_in, x_in, XSize, cudaMemcpyHostToDevice);
  cudaMemcpyAsync(dy_in, y_in, YSize, cudaMemcpyHostToDevice);
  cudaMemcpyAsync(dalpha, alpha, ASize, cudaMemcpyHostToDevice);
  cudaMemcpyAsync(dp_in, p_python, PSize, cudaMemcpyHostToDevice);
  cudaMalloc(&d_out, SubTotalMem);
	
  ///////////////// kernel launches ///////////////// 

  int dof = nSubj - 1 - num_vector_Z;
  int pt_vector_X = 0, pt_vector_Y = 0;
  int loop_it = 1, nbXVect = 0, nbYVect = 0;

  while (pt_vector_X < num_vector_X) {
    nbXVect = XVectPerCall;
    if ( pt_vector_X + XVectPerCall > num_vector_X)
      nbXVect = num_vector_X - pt_vector_X;
    pt_vector_Y=0;
		
    while(pt_vector_Y < num_vector_Y) {
      nbYVect = YVectPerCall;
      if (pt_vector_Y + YVectPerCall > num_vector_Y)
	nbYVect = num_vector_Y - pt_vector_Y;

      fprintf(stderr, "# Iteration No %d, blocks: %dx%dx%d, threads: %dx%dx%d \n",
	      loop_it, dimGrid.x, dimGrid.y, dimGrid.z, dimBlock.x, dimBlock.y, dimBlock.z);

      cudaMemset(d_out, 0 , SubTotalMem);
      cudaMemset( cmpt, 0 , sizeof(int));
      cudaMemset( flag, 0 , sizeof(int));
    
      //  cudaFuncSetCacheConfig(Kernel_DotProd,cudaFuncCachePreferL1);
      Kernel_DotProd<<< dimGrid , dimBlock, sharedMem>>>(&dx_in[pt_vector_X*VectorSize], 
							 &dy_in[pt_vector_Y*VectorSize], 
							 dp_in, d_out, dalpha, 
							 VectorSize, num_vector_Y,num_permut,
							 cmpt,dof,threshold, max_size, flag); 
      cudaGetLastError();

      // retrieve counter and flag
      cudaMemcpy(&hcmpt, cmpt, sizeof(int), cudaMemcpyDeviceToHost);
      cudaMemcpy(&hflag, flag, sizeof(int), cudaMemcpyDeviceToHost);
      
      if(hflag!=0) {
	fprintf(stderr, "# WARNING: Beta size limit was reached. Some values were not calculated.\n");
	fprintf(stderr, "Try tuning the output size with the \"divide\" parameter.\n");
	hcmpt = max_size * 80 / 100;
      }
      pt_vector_Y += YVectPerCall;
      // retrieve scores for the iteration
      cudaMemcpy(&beta[4 * total_cmpt], d_out, hcmpt * 4 * sizeof(flottant), cudaMemcpyDeviceToHost);
      total_cmpt += hcmpt;
      loop_it++;
    }
    pt_vector_X += XVectPerCall;
  }

// cleanup
cudaFree(dx_in);
cudaFree(dalpha);
cudaFree(dy_in);
cudaFree(dp_in);
cudaFree(d_out);

cudaFree(cmpt);
cudaFree(flag);

return total_cmpt;
}

/**
   Main for mulm regression
**/
int MULMRegression(flottant* X, int size_X,
		   flottant* Y, int size_Y,
		   flottant* alpha, int size_alpha,
		   int* P, int size_permut,
		   flottant* beta, int size_B,
		   int size_Z,
		   int VectorSize, int nSubj,
		   flottant divide,
		   double threshold,
		   int dev
		   )
{
  int num_vector_X = size_X / VectorSize;
  int num_vector_Y = size_Y / VectorSize;
  int num_vector_Z = size_Z / nSubj;
  int num_permut = size_permut / VectorSize;
  unsigned int values = 0;

  values = dotProdDevice(X,Y,beta,alpha,P,VectorSize, nSubj,
			 num_vector_X, num_vector_Y,num_vector_Z,num_permut,
			 divide,threshold,dev);

  return values;
}


