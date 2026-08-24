/**
 * @file led_logic.c
 * @brief Implementación de la lógica de control del LED.
 *
 * Este módulo NO accede a registros del microcontrolador; solo invoca la
 * interfaz HAL (hal_gpio_*). Eso permite cambiar de MCU (p. ej. por falta de
 * stock) implementando únicamente la capa ports/<mcu> sin tocar esta lógica.
 *
 * @requirement ICN-SW-001 La aplicación debe poder encender y apagar el LED de estado.
 * @requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón.
 * @requirement ICN-SW-003 El acceso al hardware se delega en hal_gpio_write_led.
 */

#include "led_logic.h"

static bool estado_led = false;
static bool boton_anterior = false;

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
