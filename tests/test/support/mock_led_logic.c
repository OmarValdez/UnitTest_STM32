#include "mock_led_logic.h"

#define MOCK_QUEUE_MAX 16

static bool mock_queue[MOCK_QUEUE_MAX];
static int  mock_count = 0;   /* number of queued expectations */
static int  mock_index = 0;   /* next value to return          */

/* Registro de llamadas a hal_gpio_write_led */
static bool mock_write_led_last = false;
static int  mock_write_led_count = 0;

void mock_led_logic_reset(void)
{
    mock_count = 0;
    mock_index = 0;
    mock_write_led_last = false;
    mock_write_led_count = 0;
}

void hal_gpio_write_led(bool estado)
{
    /* stub que registra la llamada para poder verificarla en el test */
    mock_write_led_last = estado;
    mock_write_led_count++;
}

void hal_gpio_read_boton_ExpectAndReturn(bool valor)
{
    /* Solo encola. El estado limpio se garantiza con mock_led_logic_reset()
       (llamado desde setUp) antes de cada test; asi no se borra el registro
       de escrituras a hal_gpio_write_led en medio de un test. */
    if (mock_count < MOCK_QUEUE_MAX)
    {
        mock_queue[mock_count] = valor;
        mock_count++;
    }
}

bool hal_gpio_read_boton(void)
{
    if (mock_count == 0)
    {
        return false;
    }

    /* Clamp to the last queued value if we run past the expectations */
    if (mock_index >= mock_count)
    {
        mock_index = mock_count - 1;
    }

    return mock_queue[mock_index++];
}

bool mock_hal_gpio_write_led_last(void)
{
    return mock_write_led_last;
}

int mock_hal_gpio_write_led_count(void)
{
    return mock_write_led_count;
}
