Compilation avec cmake :


Se placer dans un répertoire "build"

cmake 'Source_Dir' 'OPTIONS'

OPTIONS

CUDA_ROOT 		:  	path to cuda
CUDA_SDK_PATH		:	path to cuda sdk
NUMPY_INCLUDE_PATH	:	path to numpy include files
CMAKE_INSTALL_PREFIX	:	path to module to install

Source_Dir est le répertoire source contenant le CMakeLists.txt

Par exemple, sur curie :

module load cuda/4.2
module load swig
module load python/2.7.3

cmake 'chemin_vers_sources' -DCUDA_ROOT=$CUDA_ROOT -DCUDA_SDK_PATH=$CUDA_SDK_ROOT -DNUMPY_INCLUDE_PATH=/usr/local/ccc_python/stable2/lib/python2.7/site-packages/numpy/core/include -DCMAKE_VERBOSE_MAKEFILE=1 -DCMAKE_INSTALL_PREFIX='chemin'/examples

make

make install


Le module est alors créé dans le répertoire 'chemin'/examples/mulm_GPU
Il suffit alors d'ajouter ce chemin au PYTHONPATH

Par défaut, compilation avec GNU
Pour compiler avec Intel :

export CC=icc
export CXX=icpc

cmake 'chemin_vers_sources' -DCUDA_ROOT=$CUDA_ROOT -DCUDA_SDK_PATH=$CUDA_SDK_ROOT -DNUMPY_INCLUDE_PATH=/usr/local/ccc_python/stable2/lib/python2.7/site-packages/numpy/core/include -DCMAKE_VERBOSE_MAKEFILE=1 -DCMAKE_INSTALL_PREFIX='chemin'/examples
make
make install


