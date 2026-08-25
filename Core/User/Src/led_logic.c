/**
 * @file led_logic.c
 * @brief Implementación de la lógica de control del LED.
 *
 * Este módulo NO accede a registros del microcontrolador; solo invoca la
 * interfaz HAL (hal_gpio_*). Eso permite cambiar de MCU (p. ej. por falta de
 * stock) implementando únicamente la capa ports/mcu sin tocar esta lógica.
 *
 * @requirement ICN-SW-001 La aplicación debe poder encender y apagar el LED de estado.
 * @requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón.
 * @requirement ICN-SW-003 El acceso al hardware se delega en hal_gpio_write_led.
 */

#include "led_logic.h"

static bool estado_led = false;
static bool boton_anterior = false;

/* ---- Abstracción de hardware ----
 * En el firmware (build normal) estas funciones llaman al HAL real.
 * En pruebas unitarias (host, con -DUNIT_TEST) se omiten y las aporta
 * el mock mock_led_logic.c, evitando tirar del HAL y el conflicto de simbolos. */
#ifndef UNIT_TEST
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
#endif /* UNIT_TEST */


void led_logic_init(void) {
    estado_led = false;
    boton_anterior = false;
    hal_gpio_write_led(false);
}

void led_logic_update(void) {
    bool boton_actual = hal_gpio_read_boton();

    /* Detectar flanco de subida (botón presionado) -> ICN-SW-002 */
    if (boton_actual && !boton_anterior) {
        estado_led = !estado_led;       /* Conmuta el estado -> ICN-SW-001/002 */
        hal_gpio_write_led(estado_led); /* Delega en HAL -> ICN-SW-003 */
    }

    boton_anterior = boton_actual;
}

bool led_logic_get_estado(void) {
    return estado_led;
}
