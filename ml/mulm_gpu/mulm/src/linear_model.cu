#include "linear_model.h"

/**kernel : computation of Y.X and the score for p permutations
Selection of the scores over the threshold.
**/
// Macro definition
#define CudaAssert( X ) if ( !(X) ) { return; }

__global__ void Kernel_DotProd(const flottant* d_X,
			const flottant* d_Y,
			const int* d_P,
			flottant *d_out,
			flottant *dalpha,
			int	Yoffset,
			size_t VectorSize,
			int num_vector_X,
			int num_vector_Y,
			int num_permut,
			unsigned int *cmpt,
			int dof,
			int threshold,
			int max_size,
			unsigned int *flag
			)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
{
	extern __shared__ flottant shared[];
	flottant *Y = &shared[0];
	flottant *X = &shared[TILE_WIDTH*blockDim.y];
	__shared__ int P[TILE_WIDTH*BLOCK_SIZEY];
	__shared__ flottant A[BLOCK_SIZEY];
	flottant results=0;
	flottant dot=0;
	int x_id = blockIdx.x;
	int y_id = blockIdx.y*blockDim.y + threadIdx.y;
	int z_id = blockIdx.z*blockDim.z + threadIdx.z;
	int intVectorSize = (VectorSize/TILE_WIDTH)*TILE_WIDTH;
	int restVectorSize = VectorSize%TILE_WIDTH;
	int ii, ind;
	int indx;
	CudaAssert( ( (*cmpt) < max_size ) );
	for(int k=0; k<VectorSize; k++)
		X[k]=d_X[x_id*VectorSize+k];
	X[VectorSize]=0;

	A[threadIdx.z]=dalpha[x_id*num_permut+z_id];

	for(ii=0;ii<intVectorSize;ii+=TILE_WIDTH)
	{
		for(int k=0; k<blockDim.y; k++)
			for(int j=0; j<TILE_WIDTH; j+=blockDim.y)
				Y[k*TILE_WIDTH + j + threadIdx.y]=d_Y[(blockIdx.y*blockDim.y + k)*VectorSize + ii + j + threadIdx.y];
		for(int k=0; k<blockDim.z; k++)
			for(int j=0; j<TILE_WIDTH; j+=blockDim.z)
				P[k*TILE_WIDTH + j + threadIdx.z]=d_P[(blockIdx.z*blockDim.z + k)*VectorSize + ii + j + threadIdx.z];
		__syncthreads();

	
		for(int j=0;j<TILE_WIDTH;j++)
		{
			ind=P[j+threadIdx.z*TILE_WIDTH];
			dot+= X[ind]*Y[j+threadIdx.y*TILE_WIDTH];
		}
		__syncthreads();
	}
	int j=0;
	ii=intVectorSize;
	if(restVectorSize)
	{
		for(int k=0; k<blockDim.y; k++)
				Y[k*restVectorSize+j+(threadIdx.y%restVectorSize)]=d_Y[(blockIdx.y*blockDim.y+k)*VectorSize+ii+j+(threadIdx.y%restVectorSize)];
		for(int k=0; k<blockDim.z; k++)
				P[k*restVectorSize+j+(threadIdx.z%restVectorSize)]=d_P[(blockIdx.z*blockDim.z+k)*VectorSize+ii+j+(threadIdx.z%restVectorSize)];
		__syncthreads();
		for(int j=0;j<restVectorSize;j++)
		{
			ind=P[j+threadIdx.z*restVectorSize];
			dot+= X[ind]*Y[j+threadIdx.y*restVectorSize];
		}
	}
	
	results = (dof*dot*dot)/(1-A[threadIdx.z]-dot*dot);
	if((abs(results) > threshold)){
		CudaAssert( ( *cmpt < max_size ) );
		indx = atomicInc(cmpt,num_vector_X*num_vector_Y*num_permut ); //valeur max : 2^31-1
		//indx = atomicAdd(cmpt,1);
		(*flag)|=(indx > max_size - 1) ;
		if(indx<max_size)
		{
		d_out[indx*4] = results;
		d_out[indx*4 + 1] = x_id;
		d_out[indx*4 + 2] = y_id;
		d_out[indx*4 + 3] = z_id;
	}}
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/** Set CUDA environment, device, etc
Set block and grid size
Allocate, initialize and copy memory to device
Launch kernel.
**/

int  dotProdDevice(const flottant *x_in, 
			const flottant *y_in,
			const flottant *z_in,
			flottant *beta, 
			flottant *alpha,
			int *p_python,
			size_t VectorSize, 
			int num_vector_X,
			int num_vector_Y,
			int num_vector_Z,
			int num_permut,
			flottant divide,
			int threshold,
			int dev
			)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
{
	flottant *dx_in;
	flottant *dy_in;
	flottant *dalpha;
	int *dp_in;
	int *p_in;
	flottant *d_out;
	unsigned int *cmpt;
	unsigned int *flag;
	unsigned int hcmpt;
	unsigned int hflag;
	unsigned int total_cmpt = 0;
	size_t YSize = num_vector_Y*VectorSize*sizeof(flottant);
	size_t XSize = num_vector_X*VectorSize*sizeof(flottant);
	size_t PSize = num_permut*VectorSize*sizeof(int);
	size_t ASize = num_vector_X*num_permut*sizeof(flottant);
	size_t TotalSize = (num_vector_X*num_vector_Y)*(divide)*sizeof(flottant);
	size_t SubTotalMem;
/******************Get Device Properties of dev 0**************************/
	int deviceNb;
	cudaGetDeviceCount(&deviceNb);
	if(dev<deviceNb)
		cudaSetDevice(dev);
	else{
		printf("%d is not a valid device Id\n", dev);
		exit(-1);
	}
	cudaDeviceProp deviceProp;
	cudaGetDeviceProperties(&deviceProp, dev);
	size_t free, total;
	cutilSafeCall(cudaMemGetInfo(&free, &total));
	size_t globalLeft = free*4/5;
	if(globalLeft< (XSize + YSize + PSize + ASize)){
		printf("Cannot allocate input data on device. Max Memory exceeded : %lu MB / %lu MB \n",(XSize + YSize + PSize + ASize)/1048576,globalLeft/1048576);
		exit(0);
	}
	else
		globalLeft-=(XSize + YSize + PSize + ASize);
		
    	printf("Total size of X, Y and P	=	%lu MB\n",(XSize + YSize + PSize)/1048576);
	printf("Global memory left after allocating X and Y	=	%lu MB\n",globalLeft/1048576);
	printf("Total global memory	 =	%lu MB\n",total/1048576);
	printf("Size needed for result array	=	 %lu MB\n",TotalSize/1048576);
 	
	int BlockSizeY = BLOCK_SIZEY;
	int BlockSizeP = BLOCK_SIZEY;
	int BlockSizeX = BLOCK_SIZEX;
		
/******************Allocation and Copy of input data**************************/
	
	int New_num_vector_Y=num_vector_Y;
	if(num_vector_Y%BlockSizeY)
		New_num_vector_Y = num_vector_Y + BlockSizeY-(num_vector_Y%BlockSizeY);
	size_t NewYSize = New_num_vector_Y*VectorSize*sizeof(flottant);
	
	int New_num_permut=num_permut;
	if(num_permut%BlockSizeP)
		New_num_permut = num_permut + BlockSizeP-(num_permut%BlockSizeP);
	size_t NewPSize = New_num_permut*VectorSize*sizeof(int);

	//p_in = (int*) realloc( p_in , NewPSize);
	p_in = (int*) malloc(NewPSize);
	for(int i=0; i<num_permut; i++)
		for (int j=0; j<VectorSize; j++)
			p_in[i*VectorSize+j] = p_python[i*VectorSize+j];
		
	for(int i=num_permut; i<New_num_permut; i++)
		for (int j=0; j<VectorSize; j++)
			p_in[i*VectorSize+j] = VectorSize;

	size_t NewASize = New_num_permut*num_vector_X*sizeof(flottant);
	//allocate memory for arrays in the device
	cutilSafeCall(cudaMalloc( &dx_in, XSize));
	cutilSafeCall(cudaMalloc( &dy_in, NewYSize));
	cutilSafeCall(cudaMalloc( &dalpha, NewASize));
	cutilSafeCall(cudaMalloc( &dp_in, NewPSize));

	cutilSafeCall(cudaMalloc( &cmpt, sizeof(int)));
	cutilSafeCall(cudaMalloc( &flag, sizeof(int)));
	
	//copy data from host to device
	cutilSafeCall(cudaMemcpyAsync(dx_in, x_in, XSize, cudaMemcpyHostToDevice));
	cutilSafeCall(cudaMemcpyAsync(dy_in, y_in, YSize, cudaMemcpyHostToDevice));
	cutilSafeCall(cudaMemset(&dy_in[num_vector_Y*VectorSize], 0 , (NewYSize- YSize)));
	cutilSafeCall(cudaMemcpyAsync(dalpha, alpha, ASize, cudaMemcpyHostToDevice));
	cutilSafeCall(cudaMemset(&dalpha[num_permut*num_vector_X], 0 , (NewASize - ASize)));

	cutilSafeCall(cudaMemcpyAsync(dp_in, p_in, NewPSize, cudaMemcpyHostToDevice));
	//cutilSafeCall(cudaMemset(&dp_in[num_permut*VectorSize], 0 , (NewPSize - PSize)));
	
	int maxGridSize0 = deviceProp.maxGridSize[0];
	int maxGridSize1 = deviceProp.maxGridSize[1];
	int maxGridSize2 = deviceProp.maxGridSize[2];
	//printf("maxGridSize  = %d\n",deviceProp.maxGridSize[0]);
	int nb_block_x = num_vector_X;
	int nb_block_y = New_num_vector_Y/BlockSizeY;
	int nb_block_p = New_num_permut/BlockSizeP;
	//size_t size = num_vector_X*New_num_vector_Y*sizeof(flottant);

	if(nb_block_x>maxGridSize0)
	{
		printf("Exceeding Max X Grid Size \n");
		nb_block_x = nb_block_x/(nb_block_x/maxGridSize0+1)+1;
	}
	if(nb_block_y>maxGridSize1)
	{
		printf("Exceeding Max Y Grid Size \n");
		nb_block_y = nb_block_y/(nb_block_y/maxGridSize1+1)+1;
	}
	if(nb_block_p>maxGridSize2)
	{
		printf("Error : Exceeding Max Z Grid Size \nCannot have num_permut bigger than %d\n",maxGridSize2);
		exit(0);
	}
	
	size_t size = (nb_block_x*BlockSizeX)*(nb_block_y*BlockSizeY)*(divide)*sizeof(flottant);

	if(size>globalLeft)
	{
		printf("Exceeding Memory Capacity \n");
		printf("current nb_blocks=%d, size=%lu B\n",nb_block_y,size);
		nb_block_y = nb_block_y/(size/globalLeft+1)+1;
		printf("size/globalLeft+1=%lu, new nb_block=%d\n",size/globalLeft+1,nb_block_y);
	}

	int XVectPerCall=nb_block_x*BlockSizeX;
	int YVectPerCall=nb_block_y*BlockSizeY;
	printf("number of Xvectors per call = %d\nnumber of Yvectors per call = %d\n",XVectPerCall,YVectPerCall);
	int nbXVect,nbYVect;

	SubTotalMem = (XVectPerCall*YVectPerCall)*(divide)*sizeof(flottant);
	//printf("d_out memory allocated = %lu\n", SubTotalMem);
	cutilSafeCall(cudaMalloc( &d_out, SubTotalMem));
	int dof=VectorSize - 1 - num_vector_Z;
	int pt_vector_X=0, pt_vector_Y=0;
	dim3 dimBlock(BlockSizeX, BlockSizeY, BlockSizeP);
	dim3 dimGrid(nb_block_x, nb_block_y, nb_block_p);
	
/********************kernel launches**************************/
	while (pt_vector_X<num_vector_X){
		nbXVect = XVectPerCall;
		if ( pt_vector_X + XVectPerCall > num_vector_X)
			nbXVect = num_vector_X - pt_vector_X;
		pt_vector_Y=0;
		
		while(pt_vector_Y<New_num_vector_Y){
			nbYVect = YVectPerCall;
			if ( pt_vector_Y + YVectPerCall > New_num_vector_Y)
				nbYVect = New_num_vector_Y - pt_vector_Y;
			printf("Number of vectors treated in this loop = %dx%d\n", nbXVect,nbYVect);
			printf("##############\n");
			printf("Number of threads	=	%dx%dx%d \n"\
				 "Number of blocks	=	%dx%dx%d \n"\
				 ,dimBlock.x, dimBlock.y, dimBlock.z, dimGrid.x, dimGrid.y, dimGrid.z);
			printf("##############\n");

			cutilSafeCall(cudaMemset(d_out, 0 , SubTotalMem));
			cutilSafeCall(cudaMemset( cmpt, 0 , sizeof(int)));
			cutilSafeCall(cudaMemset( flag, 0 , sizeof(int)));
			size_t max_size = (XVectPerCall*YVectPerCall)*(divide/4);
			printf("Maximum number of values allowed = %G\n", (double)max_size);
			size_t sharedMem = (VectorSize + 1 + TILE_WIDTH*BlockSizeY)*sizeof(flottant);
			Kernel_DotProd<<< dimGrid , dimBlock, sharedMem>>>(&dx_in[pt_vector_X*VectorSize], &dy_in[pt_vector_Y*VectorSize], dp_in, d_out,dalpha, pt_vector_Y, VectorSize, num_vector_X, New_num_vector_Y,New_num_permut,cmpt,dof,threshold, max_size, flag); 
			cutilSafeCall(cudaGetLastError());
			cutilSafeCall(cudaMemcpy(&hcmpt, cmpt, sizeof(int), cudaMemcpyDeviceToHost));
			cutilSafeCall(cudaMemcpy(&hflag, flag, sizeof(int), cudaMemcpyDeviceToHost));
			printf("flag = %d\n", hflag);
			if(hflag!=0){
				 printf("############\nWARNING");
				 printf(" : Beta size limit was reached. Some values were not calculated.\nTry tuning the output size with the \"divide\" parameter.\n");
				 printf("############\n");
				 hcmpt=max_size*80/100;
			}
			pt_vector_Y += YVectPerCall;
//			printf("Max number of values =  %G\nnumber of values calculated in this launch : %d\n", (double)max_size,hcmpt);
			cutilSafeCall(cudaMemcpy(&beta[4*total_cmpt], d_out, hcmpt*4*sizeof(flottant), cudaMemcpyDeviceToHost));
			total_cmpt += hcmpt;
		}
		pt_vector_X += XVectPerCall;
	}
	printf("number of calculated values =	%G\n",(double)total_cmpt);

	printf("DotProd done\n");
	// cleanup
	cudaFree(p_in);
	cudaFree (dx_in);
	cudaFree (dy_in);
	cudaFree (dp_in);
	cudaFree (d_out);

	return total_cmpt;
}

/**Main for mulm regression called by run_mulm_permut.py
**/
int MULMRegression(flottant* X, int size_X,
		   flottant* Y, int size_Y,
		   flottant* Z, int size_Z,
		   int* P, int size_permut,
		   int VectorSize,
		   flottant divide,
		   int threshold,
		   flottant* beta, int size_B,
		   int dev
		   )
{
	int num_vector_X=size_X/VectorSize;
	int num_vector_Y=size_Y/VectorSize;
	int num_vector_Z=size_Z/VectorSize;
	int num_permut=size_permut/VectorSize;

	
	printf("Arguments : \n");
	printf("num_vector_X/Y/Z : %d, %d, %d\n",num_vector_X,num_vector_Y,num_vector_Z);
	printf("num_permut : %d\nVectorSize : %d\nThreshold : %d\n",num_permut,VectorSize,threshold);
		
	int lost_dof=0;
	unsigned int values = 0;
//step 1 (regression 1): extract Covariables effect from y
	lost_dof+=orthoNorm(Z, VectorSize, num_vector_Z);
	
	normalize(Y, VectorSize, num_vector_Y);

	proj(Y, Z, VectorSize, num_vector_Y, num_vector_Z);
	normalize(Y, VectorSize, num_vector_Y);

// step 2 (regression 2): extract effect of z from x
	normalize(X, VectorSize, num_vector_X);

	proj(X, Z, VectorSize, num_vector_X, num_vector_Z);
	normalize(X, VectorSize, num_vector_X);

	flottant *alpha=(flottant*)calloc(num_vector_Y*num_permut,sizeof(flottant));
	if(alpha==NULL){
		printf("Error : couldn't allocate alpha\n");
		exit(0);
	}
	beta=(flottant*)malloc(size_B*sizeof(flottant));
	if(beta==NULL){
		printf("Error : couldn't allocate beta\n");
		exit(0);
	}
//  step 4: original regression (3)
	dotProdPerm(Y, Z, P, alpha, VectorSize, num_vector_Y, num_vector_Z, num_permut);
	values = dotProdDevice(Y,X,Z,beta,alpha,P,VectorSize,num_vector_Y, num_vector_X,num_vector_Z,num_permut,divide,threshold,dev);

#ifdef DISPLAY
	SaveMat(beta,4,values, "beta");
	flottant *mean_scores = (flottant*)calloc(num_permut*4,sizeof(flottant));
	flottant *count = (flottant*)calloc(num_permut,sizeof(flottant));
	for(int i=0; i<num_permut*4; i++)
		mean_scores[i]=0;
// on prend le beta max pour chaque permut		
	for(int i=0; i<values; i++){
		if(beta[4*i] > mean_scores[(int)beta[4*i+3]*4+1]){
			mean_scores[(int)beta[4*i+3]*4+1] = beta[4*i];
			mean_scores[(int)beta[4*i+3]*4+2] = beta[4*i+1];
			mean_scores[(int)beta[4*i+3]*4+3] = beta[4*i+2];
		}
//on prend la moyenne des betas pour une permut
		mean_scores[(int)beta[4*i+3]*4]+=beta[4*i];
		count[(int)beta[4*i+3]]++;
	}
	for(int i=0; i<num_permut; i++)
		mean_scores[i*4]/=count[i];
	SaveMat(mean_scores,4,num_permut,"mean_scores");
#endif
	free(alpha);	
	printf("end of MulmRegression call\n");
	free(beta);
	return values;
}


