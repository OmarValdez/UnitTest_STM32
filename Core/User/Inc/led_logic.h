/**
 * @file led_logic.h
 * @brief Lógica de control del LED y abstracción de hardware.
 *
 * @requirement ICN-SW-001 La aplicación debe poder encender y apagar el LED de estado.
 * @requirement ICN-SW-002 El estado del LED debe conmutar únicamente en el flanco de
 *                subida del botón (no mientras permanece presionado).
 * @requirement ICN-SW-003 El cambio de estado del LED debe delegar en la capa HAL
 *                (hal_gpio_write_led), de modo que el hardware sea intercambiable.
 */

#ifndef LED_LOGIC_H
#define LED_LOGIC_H

#include <stdbool.h>

/* ---- Abstraccion de hardware (HAL) del LED/boton ----
 * En el firmware estas funciones se implementan en led_logic.c llamando
 * directo al HAL de STM32. En pruebas unitarias (host, con -DUNIT_TEST)
 * se omiten y las aporta el mock mock_led_logic.c. */
void hal_gpio_write_led(bool estado);
bool hal_gpio_read_boton(void);

/* ---- Lógica de la aplicación (independiente del microcontrolador) ---- */
void led_logic_init(void);
void led_logic_update(void);
bool led_logic_get_estado(void);

#endif /* LED_LOGIC_H */
