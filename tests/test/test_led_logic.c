#include "unity.h"
#include "led_logic.h"
#include "mock_led_logic.h"

/* Ceedling ejecuta setUp() antes de cada test, asi todas las pruebas
 * arrancan desde un estado conocido (mock limpio + led_logic inicializado). */
void setUp(void)
{
    mock_led_logic_reset();
    led_logic_init();
}

/** ICN-SW-001: al iniciar el LED debe estar apagado y la HAL debe haber
 * recibido exactamente una escritura con valor false.
 * @requirement ICN-SW-001 La aplicación debe poder encender y apagar el LED de estado.
 * @requirement ICN-SW-003 El acceso al hardware se delega en hal_gpio_write_led. */
void test_led_logic_init_debe_apagar_led(void) {
    TEST_ASSERT_FALSE(led_logic_get_estado());
    TEST_ASSERT_EQUAL(1, mock_hal_gpio_write_led_count());
    TEST_ASSERT_FALSE(mock_hal_gpio_write_led_last());
}

/** ICN-SW-002: un flanco de subida (boton presionado) conmuta el LED.
 * @requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón. */
void test_led_logic_update_boton_presionado_cambia_estado(void) {
    hal_gpio_read_boton_ExpectAndReturn(true);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
    TEST_ASSERT_TRUE(mock_hal_gpio_write_led_last());
}

/** ICN-SW-002: al soltar (flanco de bajada) el LED NO conmuta.
 * @requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón. */
void test_led_logic_update_boton_suelto_no_cambia_estado(void) {
    hal_gpio_read_boton_ExpectAndReturn(true);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
    TEST_ASSERT_TRUE(mock_hal_gpio_write_led_last());

    hal_gpio_read_boton_ExpectAndReturn(false);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
    TEST_ASSERT_TRUE(mock_hal_gpio_write_led_last());
}

/** ICN-SW-002: mientras el boton se mantiene presionado NO se conmuta
 * repetidamente (la conmutacion es solo en flanco de subida).
 * @requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón. */
void test_led_logic_update_boton_mantenido_no_repit_e(void) {
    hal_gpio_read_boton_ExpectAndReturn(true);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
    TEST_ASSERT_TRUE(mock_hal_gpio_write_led_last());

    hal_gpio_read_boton_ExpectAndReturn(true);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());   /* sigue igual */
    TEST_ASSERT_TRUE(mock_hal_gpio_write_led_last());
}

/** ICN-SW-001/002: dos pulsaciones (con un suelta entre medio) conmutan
 * dos veces: enciende y luego apaga.
 * @requirement ICN-SW-001 La aplicación debe poder encender y apagar el LED de estado.
 * @requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón. */
void test_led_logic_update_boton_presionado_dos_veces_cambia_dos_veces(void) {
    hal_gpio_read_boton_ExpectAndReturn(true);
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());
    TEST_ASSERT_TRUE(mock_hal_gpio_write_led_last());

    hal_gpio_read_boton_ExpectAndReturn(false);  /* suelta: sin cambio */
    led_logic_update();
    TEST_ASSERT_TRUE(led_logic_get_estado());

    hal_gpio_read_boton_ExpectAndReturn(true);   /* nueva pulsacion */
    led_logic_update();
    TEST_ASSERT_FALSE(led_logic_get_estado());
    TEST_ASSERT_FALSE(mock_hal_gpio_write_led_last());
}
