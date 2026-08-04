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
    
    // Detectar flanco de subida (botón presionado)
    if (boton_actual && !boton_anterior) {
        estado_led = !estado_led;  // Cambia el estado del LED
        hal_gpio_write_led(estado_led);
    }
    
    boton_anterior = boton_actual;
}

bool led_logic_get_estado(void) {
    return estado_led;
}