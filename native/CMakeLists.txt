cmake_minimum_required(VERSION 3.20)
project(TaskWeaveNative VERSION 0.1.0 LANGUAGES CXX)

add_executable(taskweave_native src/main.cpp)
target_include_directories(taskweave_native PRIVATE include)
target_compile_features(taskweave_native PRIVATE cxx_std_20)

if(MSVC)
    target_compile_options(taskweave_native PRIVATE /W4 /permissive-)
else()
    target_compile_options(taskweave_native PRIVATE -Wall -Wextra -Wpedantic)
endif()

enable_testing()
add_test(NAME native_queue_demo COMMAND taskweave_native)