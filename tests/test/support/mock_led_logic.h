#ifndef MOCK_LED_LOGIC_H
#define MOCK_LED_LOGIC_H

#include <stdbool.h>

/* Real hardware abstraction functions (implemented by the mock) */
void hal_gpio_write_led(bool estado);
bool hal_gpio_read_boton(void);

/* CMock-style expectation API used by the tests */
void hal_gpio_read_boton_ExpectAndReturn(bool valor);

/* Optional reset hook (callable from a custom setUp if desired) */
void mock_led_logic_reset(void);

/* Accesores para verificar que hal_gpio_write_led fue llamada:
 *  - mock_hal_gpio_write_led_last()  -> ultimo valor escrito
 *  - mock_hal_gpio_write_led_count() -> nro de veces que se escribio */
bool mock_hal_gpio_write_led_last(void);
int  mock_hal_gpio_write_led_count(void);

#endif /* MOCK_LED_LOGIC_H */
