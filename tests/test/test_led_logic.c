#include "unity.h"
#include "led_logic.h"
#include "mock_led_logic.h"

void test_led_logic_init_debe_apagar_led(void) {
    led_logic_init();
    TEST_ASSERT_FALSE(led_logic_get_estado());
}

void test_led_logic_update_boton_presionado_cambia_estado(void) {
    hal_gpio_read_boton_ExpectAndReturn(true);
    
    led_logic_init();
    led_logic_update();
    
    TEST_ASSERT_TRUE(led_logic_get_estado());
}

void test_led_logic_update_boton_suelto_no_cambia_estado(void) {
    // Primero presionar
    hal_gpio_read_boton_ExpectAndReturn(true);
    led_logic_init();
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
    
    // Luego soltar
    hal_gpio_read_boton_ExpectAndReturn(false);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
}

void test_led_logic_update_boton_presionado_dos_veces_cambia_dos_veces(void) {
    led_logic_init();
    TEST_ASSERT_FALSE(led_logic_get_estado());
    
    // Primera presión: encender
    hal_gpio_read_boton_ExpectAndReturn(true);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
    
    // Segunda presión: apagar (simular que el botón se suelta y presiona de nuevo)
    // Nota: En la lógica real, entre presión y presión debe haber un "suelta"
    hal_gpio_read_boton_ExpectAndReturn(false); // Simular que se suelta
    led_logic_update(); // Esto no debería cambiar el estado
    
    hal_gpio_read_boton_ExpectAndReturn(true); // Simular que se presiona de nuevo
    led_logic_update();
    TEST_ASSERT_FALSE(led_logic_get_estado());
}