#include "linear_model.h"
/**
   kernel : computation of Y.X and the score for p permutations
**/
// Macro definition
#define CudaAssert( X )  if ( !(X) ) { return; }

#define	BLOCK_SIZEX	1

#define	BLOCK_SIZEY 32
#define bsize 64
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
			       double *d_out,
			       const size_t VectorSize,
			       const int num_vector_Y,
			       const int num_vector_X)
{
  extern __shared__ flottant shared[];
  flottant *X = &shared[0];
  __shared__ double dot[nb_permut_per_th*bsize];
  flottant Y;
  int tid= threadIdx.z+threadIdx.y*blockDim.z;
  int y_id = blockIdx.y*blockDim.y + threadIdx.y;
  int z_id = blockIdx.z*blockDim.z + threadIdx.z;
  unsigned int ind, k;
  double b2;
  // the block of threads loads X
  for(int i=0; i<num_vector_X; i++) {

    // initialize dot[] to 0
    for(int j=0;j<nb_permut_per_th;j++)
      dot[j*bsize+tid]=0;

    for(k=0; k<VectorSize; k+=blockDim.z*blockDim.y)
      if((k+threadIdx.y+threadIdx.z*blockDim.y)<VectorSize)
	X[k+threadIdx.y+threadIdx.z*blockDim.y]=d_X[(blockIdx.x+i)*VectorSize+k+threadIdx.y+threadIdx.z*blockDim.y];

    __syncthreads(); // wait until data are loaded
  
    // dot(X[perm],Y), ie. beta computation
    for(k=0;k<VectorSize;k++)
      {
	Y=d_Y[num_vector_Y*(k)+y_id];
	for(int j=0;j<nb_permut_per_th;j++)
	  {
	    ind=d_P[(nb_permut_per_th*z_id+j)*VectorSize+k];
	    dot[j*bsize+tid]+= X[ind]*Y;
	  }
      }
    
    for(int j=0;j<nb_permut_per_th;j++) {
      b2 = dot[j*bsize+tid] * dot[j*bsize+tid];
      d_out[(j+nb_permut_per_th*z_id)* num_vector_Y + y_id] += b2;

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
void dotProdDevice(const flottant *x_in, 
		   const flottant *y_in,
		   double *beta,
		   int *p_python,
		   size_t VectorSize,
		   int num_vector_X,
		   int num_vector_Y,
		   int num_permut,
		   int dev
		   )
{
  flottant *dx_in;
  flottant *dy_in;
  int *dp_in;
  double *d_out;
  size_t YSize = num_vector_Y * VectorSize * sizeof(flottant);
  size_t XSize = num_vector_X * VectorSize * sizeof(flottant);
  size_t PSize = num_permut * VectorSize * sizeof(int);
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
  if(globalLeft < (XSize + YSize + PSize)) {
    fprintf(stderr, "# Cannot allocate input data on device. Max Memory exceeded : %lu MB / %lu MB \n",
	    (XSize + YSize + PSize) / 1048576, globalLeft / 1048576);
    exit(0);
  } else 
    globalLeft -= (XSize + YSize + PSize);
 	
  int BlockSizeY = BLOCK_SIZEY;
  int BlockSizeP = bsize / BLOCK_SIZEY;
  int BlockSizeX = BLOCK_SIZEX;
	
  int maxGridSize1 = deviceProp.maxGridSize[1];
  int maxGridSize2 = deviceProp.maxGridSize[2];

  int nb_block_x = 1; // num_vector_X;
  int nb_block_y = num_vector_Y / BlockSizeY;
  int nb_block_p = num_permut / BlockSizeP;

  if(nb_block_y > maxGridSize1) {
    fprintf(stderr, "# Exceeding Max Y Grid Size \n");
    nb_block_y = nb_block_y / (nb_block_y / maxGridSize1 + 1) + 1;
  }
  if(nb_block_p > maxGridSize2) {
    fprintf(stderr, "# Error : Exceeding Max Z Grid Size \nCannot have num_permut bigger than %d\n",maxGridSize2);
    exit(0); 
  }

   size_t size = nb_block_y * BlockSizeY * nb_block_p * BlockSizeP * sizeof(flottant);

  if(size > globalLeft) {
    fprintf(stderr, "# Exceeding GPU Memory Capacity \n");
    nb_block_y = nb_block_y / (size / globalLeft + 1) + 1;
    fprintf(stderr, "# Number of GPU iterations needed =  %lu\n", size / globalLeft + 1);
  }

  int XVectPerCall = nb_block_x * BlockSizeX;
  int YVectPerCall = nb_block_y * BlockSizeY;

  dim3 dimBlock(BlockSizeX, BlockSizeY, BlockSizeP);
  dim3 dimGrid(nb_block_x, nb_block_y, nb_block_p / nb_permut_per_th);

  SubTotalMem = YVectPerCall * nb_block_p * BlockSizeP * sizeof(double);
  fprintf(stderr, "# d_out memory allocated = %lu\n", SubTotalMem);

  size_t sharedMem = ((VectorSize / 32) * 32) * sizeof(flottant);
  fprintf(stderr,"# SharedMem = %G\n", (double)sharedMem);

  ///////////////// Allocation and Copy of input data ////////////////

  // allocate memory for arrays in the device
 cudaMalloc( &dx_in, XSize);
 cudaMalloc( &dy_in, YSize);
 cudaMalloc( &dp_in, PSize);
	
  //copy data from host to device
  cudaMemcpyAsync(dx_in, x_in, XSize, cudaMemcpyHostToDevice);
  cudaMemcpyAsync(dy_in, y_in, YSize, cudaMemcpyHostToDevice);
  cudaMemcpyAsync(dp_in, p_python, PSize, cudaMemcpyHostToDevice);
  cudaMalloc(&d_out, SubTotalMem);
  	
  ///////////////// kernel launches ///////////////// 

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

      //  cudaFuncSetCacheConfig(Kernel_DotProd,cudaFuncCachePreferL1);
      Kernel_DotProd<<< dimGrid , dimBlock, sharedMem>>>(&dx_in[pt_vector_X*VectorSize], 
							 &dy_in[pt_vector_Y*VectorSize], 
							 dp_in, d_out,
							 VectorSize, num_vector_Y,
							 num_vector_X); 
      cudaGetLastError();
      pt_vector_Y += YVectPerCall;
      // retrieve scores for the iteration
      cudaMemcpy(beta, d_out, SubTotalMem, cudaMemcpyDeviceToHost);
      loop_it++;
    }
    pt_vector_X += num_vector_X;
  }
  
  // cleanup
  cudaFree(dx_in);
  cudaFree(dy_in);
  cudaFree(dp_in);
  cudaFree(d_out);
}

/**
   Main for mulm regression
**/
int OLSRegression(flottant* X, int size_X,
		   flottant* Y, int size_Y,
		   int* P, int size_permut,
		   double* beta, int size_B,
		   int VectorSize,
		   int dev
		   )
{
  int num_vector_X = size_X / VectorSize;
  int num_vector_Y = size_Y / VectorSize;
  int num_permut = size_permut / VectorSize;

  dotProdDevice(X,Y,beta,P,VectorSize,
		num_vector_X, num_vector_Y, num_permut, dev);
  return 0;
}


