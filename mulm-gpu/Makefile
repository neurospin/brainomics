
############# CUDA #############
CUDAPATH=$(CUDA_ROOT)
SDKPATH=$(CUDA_SDK_ROOT)

############ Python ############
#PYTHON_INC=/usr/include/$(PYTHON_VER)
#NUMPY_INC=$(PYTHONPATH)/site-packages/numpy/core/include
PY_INC=$(PYTHON_INC)
NU_INC=$(NUMPY_INC)

OBJ=./build
SRC=./src
SRC_CORR=./src/mu-corr
N_CORR=linear_model
N_OLS=linear_model_ols
SRC_OLS=./src/mu-ols
BUILD=./build
INC=./include

########## Compilation ####

CC=icpc
NVCC=nvcc

#### Flags ####

#DISP=-DDISPLAY
#DEBUG=-g -G
CCF=-O3 -fPIC $(DISP) $(DEBUG)
NVCCF=-O3 -Xcompiler -fPIC -arch=sm_21 $(DISP) $(DEBUG)
LDFLAGS=-L$(SDKPATH)/lib -L$(CUDAPATH)/lib64 -lcutil_x86_64 -lcuda -lcudart

all : $(BUILD) $(BUILD)/_$(N_CORR).so $(BUILD)/_$(N_OLS).so
	touch $(BUILD)/__init__.py

$(BUILD):
	mkdir build

$(BUILD)/_$(N_CORR).so :
	swig -python -c++ -I$(INC) $(SRC_CORR)/$(N_CORR).i
	mv $(SRC_CORR)/$(N_CORR).py $(BUILD)
	$(CC) -c $(CCF) -o $(OBJ)/$(N_CORR)_wrap.o $(SRC_CORR)/$(N_CORR)_wrap.cxx -I$(INC) -I$(PY_INC) -I$(NU_INC)
	$(NVCC) -c $(NVCCF) -o $(OBJ)/$(N_CORR).o $(SRC_CORR)/$(N_CORR).cu \
		-I$(CUDAPATH)/include -I$(SDKPATH)/common/inc/ -I$(INC)
	$(CC) -shared -O3 -o $(BUILD)/_$(N_CORR).so $(OBJ)/$(N_CORR).o $(OBJ)/$(N_CORR)_wrap.o $(LDFLAGS)

$(BUILD)/_$(N_OLS).so :
	swig -python -c++ -I$(INC) $(SRC_OLS)/$(N_OLS).i
	mv $(SRC_OLS)/$(N_OLS).py $(BUILD)
	$(CC) -c $(CCF) -o $(OBJ)/$(N_OLS)_wrap.o $(SRC_OLS)/$(N_OLS)_wrap.cxx -I$(INC) -I$(PY_INC) -I$(NU_INC)
	$(NVCC) -c $(NVCCF) -o $(OBJ)/$(N_OLS).o $(SRC_OLS)/$(N_OLS).cu \
		-I$(CUDAPATH)/include -I$(SDKPATH)/common/inc/ -I$(INC)
	$(CC) -shared -O3 -o $(BUILD)/_$(N_OLS).so $(OBJ)/$(N_OLS).o $(OBJ)/$(N_OLS)_wrap.o $(LDFLAGS)

clean :
	rm $(OBJ)/*
	rm $(SRC_CORR)/$(N_CORR)_wrap.*
	rm $(SRC_OLS)/$(N_OLS)_wrap.*
