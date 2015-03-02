project(brainomics)

cmake_minimum_required(VERSION 2.8)

find_package(CUDA REQUIRED)
find_package(SWIG REQUIRED)
find_package(PythonLibs)

set(CUDA_NVCC_FLAGS -O3 -Xcompiler -fPIC -arch=sm_21 )
set(CMAKE_MODULE_LINKER_FLAGS "-L${CUDA_SDK_PATH}/lib -L${CUDA_ROOT}/lib64")
set(LIBS ${LIBS} "-lcutil_x86_64 -lcuda -lcudart")

include(${SWIG_USE_FILE})
include_directories(${PYTHON_INCLUDE_PATH})
include_directories(${NUMPY_INCLUDE_PATH})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

cuda_include_directories(${CUDA_SDK_PATH}/common/inc)
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/src/)

install(FILES ${CMAKE_BINARY_DIR}/src/linear_model.py ${CMAKE_BINARY_DIR}/src/_linear_model.so ${CMAKE_SOURCE_DIR}/src/__init__.py DESTINATION mulm_GPU)

