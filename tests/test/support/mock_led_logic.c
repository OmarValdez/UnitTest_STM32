#include "mock_led_logic.h"

#define MOCK_QUEUE_MAX 16

static bool mock_queue[MOCK_QUEUE_MAX];
static int  mock_count = 0;   /* number of queued expectations */
static int  mock_index = 0;   /* next value to return          */

void mock_led_logic_reset(void)
{
    mock_count = 0;
    mock_index = 0;
}

void hal_gpio_write_led(bool estado)
{
    (void)estado; /* stub: nothing to do in the host/sim environment */
}

void hal_gpio_read_boton_ExpectAndReturn(bool valor)
{
    /* If the previous expectation sequence was fully consumed, start a new one.
       This keeps the mock stateless across separate tests. */
    if (mock_index >= mock_count)
    {
        mock_led_logic_reset();
    }

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
