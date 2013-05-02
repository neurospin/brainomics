cuda_compile(CUDA_OBJECTS linear_model.cu)

set_source_files_properties(linear_model.i PROPERTIES CPLUSPLUS ON)
swig_add_module(linear_model python linear_model.i ${CUDA_OBJECTS} mulm_utils.c++)
#set_target_properties(linear_model PROPERTIES OUTPUT_NAME ${CMAKE_CURRENT_BINARY_DIR}/lib/_linear_model.so)
swig_link_libraries(linear_model "${LIBS}") 
