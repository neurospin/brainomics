int MULMRegression(float* X, int size_X,
		   float* Y, int size_Y, 
		   float* alpha, int size_alpha, 
		   int* P, int size_P, 
		   float* beta, int max_beta, 
		   int size_Z, 
		   int VectorSize, int nSubj,
		   float divide, 
		   double threshold, 
		   int dev ); 
int get_block_sizey();
int get_bsize();
int get_nb_permut_per_th();
