cmake_minimum_required(VERSION 3.10)
project(DocumentEncryption)

set(CMAKE_CXX_STANDARD 11)

find_package(OpenSSL REQUIRED)

include_directories(${OPENSSL_INCLUDE_DIR})

add_executable(DocumentEncryption encrypt_decrypt_doc.cpp)
target_link_libraries(DocumentEncryption ${OPENSSL_LIBRARIES})
