# Especificación de Requisitos de Software (SRS)

Requisitos funcionales del firmware piloto, alineados con IEC 62304. Cada
requisito se traza automáticamente a su implementación y a sus pruebas unitarias
mediante la etiqueta `@requirement`; la página **Requisitos** de la documentación
Doxygen agrupa todas las referencias (código + tests) de cada ID.

@requirement ICN-SW-001 La aplicación debe poder encender y apagar el LED de estado.
@requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón.
@requirement ICN-SW-003 El acceso al hardware se delega en hal_gpio_write_led.

## Trazabilidad (requisito -> implementación -> verificación)

| ID | Implementación | Prueba(s) |
|----|----------------|-----------|
| ICN-SW-001 | `led_logic_init`, `led_logic_update` (`Core/User/Src/led_logic.c`) | `test_led_logic_init_debe_apagar_led`, `test_led_logic_update_boton_presionado_dos_veces_cambia_dos_veces` |
| ICN-SW-002 | `led_logic_update` (detección de flanco) | `test_led_logic_update_boton_presionado_cambia_estado`, `test_led_logic_update_boton_suelto_no_cambia_estado`, `test_led_logic_update_boton_mantenido_no_repit_e`, `test_led_logic_update_boton_presionado_dos_veces_cambia_dos_veces` |
| ICN-SW-003 | `hal_gpio_write_led` (capa ports/mcu) | `test_led_logic_init_debe_apagar_led` (verifica la escritura a la HAL) |
