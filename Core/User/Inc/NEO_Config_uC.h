/*
 * NEO_Config_uC.h
 *
 *  Created on: 27 jul 2026
 *      Author: Ruben Valdez
 */
/*
 * @file NEO_Config_uC.h
 *
 * @brief API de abstraccion de hardware
 * El proposito de esta libreria es poder desacopar el hardware y software
 * especifico de un IDE, con el objetivo de que la logica del programa cambie
 * en lo minimo posible.
 * Esta libreria no contempla la configuracion basica de lor relojes, puesta en
 * marcha basica de perifericos, interrupciones o utilidades como DMA.
 */
#ifndef ST_UNITTEST_CORE_INC_NEO_CONFIG_UC_H_
#define ST_UNITTEST_CORE_INC_NEO_CONFIG_UC_H_

#include <stdint.h>

#define STM32

#if !defined(UNIT_TEST)
/* Build de firmware (CubeMX/arm): usa el HAL real del ST. */
#ifdef STM32
#include <main.h>
#elif defined(NXP)
#include "MKL46Z4.h"
#include "PE_Types.h"
#include "WAIT1.h"
#include "BitIoLdd13.h"
#define BitIoLdd13_DeviceData  ((LDD_TDeviceData *)PE_LDD_GetDeviceStructure(PE_LDD_COMPONENT_BitIoLdd13_ID))
#elif defined(Arduino)
//todo Agregar librerias necesareias de arduino IDE
#endif
#else
/* Build de pruebas unitarias en host (gcc/Ceedling): sin HAL.
   Se proveen tipos y defines minimos para que led_logic.c compile y el
   mock mock_led_logic.c aporte las funciones hal_gpio_*. */
typedef struct GPIO_TypeDef GPIO_TypeDef;
#ifndef LED1_PORT
#define LED1_PORT      ((GPIO_TypeDef *)0)
#define LED1_PIN       0U
#define BUTTON1_PORT   ((GPIO_TypeDef *)0)
#define BUTTON1_PIN    0U
#endif
#endif




// Funciones a abtraer
void NEO_Delay_ms(uint32_t ms);

void NEO_GPIO_Read(GPIO_TypeDef *Port, uint16_t Pin, uint8_t *state);
void NEO_GPIO_Write(GPIO_TypeDef *Port, uint16_t Pin, uint8_t state);
void NEO_GPIO_Toggle(GPIO_TypeDef *Port, uint16_t Pin);

#endif /* ST_UNITTEST_CORE_INC_NEO_CONFIG_UC_H_ */
