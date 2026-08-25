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
    /* BluePill: el LED se enciende poniendo PC13 a GND (activo-bajo).
     * estado == true  -> LED encendido -> pin a 0.
     * estado == false -> LED apagado  -> pin a 1 (open-drain, sin corriente). */
    NEO_GPIO_Write(LED1_PORT, LED1_PIN, estado ? 0u : 1u);
}

bool hal_gpio_read_boton(void) {
    uint8_t state = 0u;
    NEO_GPIO_Read(BUTTON1_PORT, BUTTON1_PIN, &state);
    /* BluePill: el boton envia GND al presionar y tiene pull-up, por lo que
     * presionado == pin a nivel bajo (activo-bajo). */
    return state == 0u;
}
