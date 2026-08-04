#ifndef LED_LOGIC_H
#define LED_LOGIC_H

#include <stdbool.h>

// Funciones de abstracción de hardware (serán mockeadas)
void hal_gpio_write_led(bool estado);
bool hal_gpio_read_boton(void);

// Lógica de la aplicación
void led_logic_init(void);
void led_logic_update(void);
bool led_logic_get_estado(void);

#endif