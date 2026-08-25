#ifndef HAL_GPIO_H
#define HAL_GPIO_H

#include <stdbool.h>

/* Capa de abstraccion de hardware (HAL) del LED/boton.
 *
 * En el firmware la implementacion vive en led_logic.c y llama a NEO_GPIO_*.
 * En las pruebas unitarias (host) esa implementacion se omite (ver UNIT_TEST
 * en led_logic.c) y es provista por el mock mock_led_logic.c, por lo que aqui
 * solo se declaran los prototipos. */
void hal_gpio_write_led(bool estado);
bool hal_gpio_read_boton(void);

#endif /* HAL_GPIO_H */
