/**
 * @file hal_gpio_stm32.c
 * @brief Implementacion de la capa ports/mcu para STM32 (HAL).
 *
 * Traduce la interfaz de hardware independiente del microcontrolador
 * (hal_gpio_*) a la API de abstraccion NEO_GPIO_* definida en
 * NEO_Config_uC.h. Asi led_logic.c puede compilarse en el firmware sin
 * conocer el MCU concreto.
 */

#include "NEO_Config_uC.h"
#include "led_logic.h"
#include "main.h"

void hal_gpio_write_led(bool estado) {
    NEO_GPIO_Write(LED1_PORT, LED1_PIN, estado ? 1u : 0u);
}

bool hal_gpio_read_boton(void) {
    uint8_t state = 0u;
    NEO_GPIO_Read(BUTTON1_PORT, BUTTON1_PIN, &state);
    return state != 0u;
}
