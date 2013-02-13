
############# CUDA #############
CUDAPATH=$(CUDA_ROOT)
SDKPATH=$(CUDA_SDK_ROOT)

############ Python ############
PYTHON_INC=$(PYTHONHOME)/include/python2.6
NUMPY_INC=$(PYTHONPATH)/site-packages/numpy/core/include

OBJ=./obj
BIN=./bin
SRC=./src
SWIG=./swig
INC=./inc

########## Compilation ####

CC=icpc
NVCC=nvcc

#### Flags ####

DISP=-DDISPLAY
#DEBUG=-g -G
CCF=-O3 -fPIC $(DISP) $(DEBUG)
NVCCF=-O3 -Xcompiler -fPIC -arch=sm_21 $(DISP) $(DEBUG)
LDFLAGS=-L$(SDKPATH)/lib -L$(CUDAPATH)/lib64 -lcutil_x86_64 -lcuda -lcudart

all : $(SWIG)/_linear_model.so

$(SWIG)/_linear_model.so : 

	swig -python -I$(INC) $(SWIG)/linear_model.i

	$(CC) -c $(CCF) -o $(OBJ)/mulm_utils.o $(SRC)/mulm_utils.c -I$(INC)

	$(CC) -c $(CCF) -o $(OBJ)/linear_model_wrap.o $(SWIG)/linear_model_wrap.c -I$(INC) -I$(PYTHON_INC) -I$(NUMPY_INC)

	$(NVCC) -c $(NVCCF) -o $(OBJ)/linear_model.o $(SRC)/linear_model.cu -I$(CUDAPATH)/include -I$(SDKPATH)/common/inc/ -I$(INC) 

	$(CC) -shared -O3 -o $(SWIG)/_linear_model.so $(OBJ)/mulm_utils.o $(OBJ)/linear_model.o $(OBJ)/linear_model_wrap.o $(LDFLAGS)

clean :
	rm $(OBJ)/*
	rm $(SWIG)/*.so $(SWIG)/linear_model_wrap.* $(SWIG)/linear_model.py*
