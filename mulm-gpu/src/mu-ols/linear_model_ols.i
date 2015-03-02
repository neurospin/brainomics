%module linear_model_ols

%{
    #define SWIG_FILE_WITH_INIT
    #include "ols_regression.h"
    double* create_array( int size ){
        double* beta = (double*)malloc((size_t) size);
        if(beta==NULL){
            printf("ERROR : Could not allocate Beta\n");
            return 0;
        }
        return beta;
    }

%}

%include "../../include/numpy.i"

%init %{
    import_array();
%}


%apply (float* IN_ARRAY1    , int DIM1) {(float* X , int size_X)};
%apply (float* IN_ARRAY1    , int DIM1) {(float* Y , int size_Y)};
%apply (int* IN_ARRAY1      , int DIM1) {(int*  P  , int size_P)};
%apply (double* ARGOUT_ARRAY1, int DIM1) {(double* beta, int max_beta)}

%include "ols_regression.h"
float* create_array( int size );

