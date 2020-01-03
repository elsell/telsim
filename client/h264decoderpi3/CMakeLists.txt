# on Fedora 30, I needed to install:
# ffmpeg-devel python3-devel boost-python3-devel
cmake_minimum_required(VERSION 3.10)

find_package(Boost 1.69 REQUIRED COMPONENTS "python37")
find_package(PythonLibs 3 REQUIRED)

message(STATUS "PYTHON_LIBRARIES = ${PYTHON_LIBRARIES}")
message(STATUS "PYTHON_INCLUDE_DIRS = ${PYTHON_INCLUDE_DIRS}")
message(STATUS "Boost_LIBRARIES = ${Boost_LIBRARIES}")
message(STATUS "Boost_INCLUDE_DIRS = ${Boost_INCLUDE_DIRS}")

set(LIBAV_LIBRARIES avcodec swscale avutil)

add_library(h264decoder SHARED h264decoder_python.cpp h264decoder.cpp)
target_include_directories(h264decoder PUBLIC "/usr/include/ffmpeg/" ${PYTHON_INCLUDE_DIRS})
target_link_libraries(h264decoder ${PYTHON_LIBRARIES} ${Boost_LIBRARIES} ${LIBAV_LIBRARIES})
