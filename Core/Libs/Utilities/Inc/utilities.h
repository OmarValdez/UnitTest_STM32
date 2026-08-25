#ifndef UTILITIES_H
#define UTILITIES_H

#include <stdint.h>

/* Ejemplo de modulo en libreria propia (alternativa robusta a GLOB).
 * Demuestra que CMake compila y enlaza lo que haya en Core/Libs/Utilities
 * sin usar file(GLOB). */
uint32_t utilities_add(uint32_t a, uint32_t b);

#endif /* UTILITIES_H */
