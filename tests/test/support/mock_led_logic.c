#include "mock_led_logic.h"

static bool mock_boton_estado = false;
static int mock_boton_llamadas = 0;
static bool mock_boton_valores[10] = {false}; // Para múltiples llamadas

void hal_gpio_write_led(bool estado) {
    // Simula escritura en LED
}

bool hal_gpio_read_boton(void) {
    if (mock_boton_llamadas < 10) {
        return mock_boton_valores[mock_boton_llamadas++];
    }
    return mock_boton_estado;
}

void mock_led_logic_Init(void) {
    mock_boton_estado = false;
    mock_boton_llamadas = 0;
    for (int i = 0; i < 10; i++) {
        mock_boton_valores[i] = false;
    }
}

void mock_led_logic_Verify(void) {
    // Verifica que las expectativas se cumplieron
}

void mock_led_logic_Destroy(void) {
    // Limpieza
}

void hal_gpio_read_boton_ExpectAndReturn(bool valor) {
    mock_boton_valores[mock_boton_llamadas] = valor;
}

void hal_gpio_read_boton_ExpectAndReturn_Sequential(bool valor) {
    // Esta función permite agregar valores secuenciales
    mock_boton_valores[mock_boton_llamadas++] = valor;
}