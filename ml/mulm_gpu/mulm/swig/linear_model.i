%module linear_model

%{
    #define SWIG_FILE_WITH_INIT
    #include "mulm_regression.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (float* INPLACE_ARRAY1, int DIM1) {(flottant* X, int size_X),(flottant* Y, int size_Y),(flottant* Z, int size_Z)}
%apply (int* IN_ARRAY1, int DIM1) {(int* P, int size_permut)}
%apply (float* ARGOUT_ARRAY1, int DIM1) {(flottant* beta, int size_B)}

%include "mulm_regression.h"

