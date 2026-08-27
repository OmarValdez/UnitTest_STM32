# Especificación de Requisitos de Software (SRS)

Requisitos funcionales del firmware piloto, alineados con IEC 62304. Cada
requisito se traza automaticamente a su implementacion y a sus pruebas unitarias
mediante la etiqueta `@requirement`; la pagina **Requisitos** de la documentacion
Doxygen agrupa todas las referencias (codigo + tests) de cada ID.

@requirement ICN-SW-001 La aplicación debe poder encender y apagar el LED de estado.
@requirement ICN-SW-002 El estado del LED conmuta solo en flanco de subida del botón.
@requirement ICN-SW-003 El acceso al hardware se delega en hal_gpio_write_led.

## Trazabilidad

La matriz completa (requisito -> implementacion -> pruebas) se genera
automaticamente desde estas etiquetas `@requirement` con el script
`ci/traceability_matrix.py`. El resultado se publica en el dashboard de Jenkins
como `build/traceability/matrix.html` (y `matrix.pdf` / `matrix.md` como evidencia).

Para ampliar la trazabilidad basta con agregar aqui mas lineas
`@requirement ID texto` y referenciarlas en el codigo y en las pruebas; la matriz
se regenera sola en el siguiente build. Las celdas "sin implementacion" o
"sin pruebas" senalan brechas de trazabilidad que conviene cerrar.
