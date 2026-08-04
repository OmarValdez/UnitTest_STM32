#ifndef MOCK_LED_LOGIC_H
#define MOCK_LED_LOGIC_H

#include <stdbool.h>

// Funciones mockeadas
void hal_gpio_write_led(bool estado);
bool hal_gpio_read_boton(void);

// Funciones para el runner
void mock_led_logic_Init(void);
void mock_led_logic_Verify(void);
void mock_led_logic_Destroy(void);

// Funciones para configurar expectativas
void hal_gpio_read_boton_ExpectAndReturn(bool valor);
void hal_gpio_read_boton_ExpectAndReturn_Sequential(bool valor);

#endif