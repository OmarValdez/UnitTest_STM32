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

#endif /* MOCK_LED_LOGIC_H */
