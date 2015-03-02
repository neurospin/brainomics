%module linear_model

%{
    #define SWIG_FILE_WITH_INIT
    #include "mulm_regression.h"
    float* create_array( int size ){
        float* beta = (float*)malloc((size_t) size);
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
%apply (float* IN_ARRAY1    , int DIM1) {(float* alpha , int size_alpha)};
%apply (int* IN_ARRAY1      , int DIM1) {(int*  P  , int size_P)};
%apply (float* ARGOUT_ARRAY1, int DIM1) {(float* beta, int max_beta)}

%include "mulm_regression.h"
float* create_array( int size );

