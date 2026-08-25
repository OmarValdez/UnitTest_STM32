cmake_minimum_required(VERSION 3.22)

#
# This file is generated only once,
# and is not re-generated if converter is called multiple times.
#
# User is free to modify the file as much as necessary
#

# Setup compiler settings
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)


# Define the build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug")
endif()

# Set the project name
set(CMAKE_PROJECT_NAME ST_UnitTest)

# Enable compile command to ease indexing with e.g. clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

# Core project settings
project(${CMAKE_PROJECT_NAME})
message("Build type: " ${CMAKE_BUILD_TYPE})

# Enable CMake support for ASM and C languages
enable_language(C ASM)

# Create an executable object type
add_executable(${CMAKE_PROJECT_NAME})

# Add STM32CubeMX generated sources
add_subdirectory(cmake/stm32cubemx)

# ---------------------------------------------------------------------------
# Libreria de usuario (alternativa robusta a GLOB_RECURSE)
# CMake compila explicitamente los .c listados y expone sus headers via
# target_include_directories(PUBLIC), asi que el ejecutable (y otras
# librerias) los ven sin configuracion extra. Agregar un archivo nuevo
# aqui requiere listarlo, pero el build es 100% reproducible.
# ---------------------------------------------------------------------------
add_library(utilities STATIC
    Core/Libs/Utilities/Src/utilities.c
)
target_include_directories(utilities PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/Core/Libs/Utilities/Inc
)

# Link directories setup
target_link_directories(${CMAKE_PROJECT_NAME} PRIVATE
    # Add user defined library search paths
)

# Add sources to executable
# Todo el codigo de usuario vive en Core/User/Src (lo generado por CubeMX
# queda en Core/Src y lo agrega cmake/stm32cubemx/CMakeLists.txt).
# GLOB_RECURSE + CONFIGURE_DEPENDS incluye automaticamente cualquier
# libreria/archivo nuevo sin editar este archivo.
file(GLOB_RECURSE USER_SOURCES CONFIGURE_DEPENDS
    Core/User/Src/*.c
)
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${USER_SOURCES}
)

# Add include paths
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    # Add user defined include paths
    ${CMAKE_CURRENT_SOURCE_DIR}/Core/User/Inc
)

# Add project symbols (macros)
target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE
    # Add user defined symbols
)

# Remove wrong libob.a library dependency when using cpp files
list(REMOVE_ITEM CMAKE_C_IMPLICIT_LINK_LIBRARIES ob)

# Add linked libraries
target_link_libraries(${CMAKE_PROJECT_NAME}
    stm32cubemx
    utilities

    # Add user defined libraries
)
