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
#define	STM32


#ifdef STM32
#include <main.h>
#elif NXP
#include "MKL46Z4.h"
#include "PE_Types.h"
#include "WAIT1.h"
#include "BitIoLdd13.h"
#define BitIoLdd13_DeviceData  ((LDD_TDeviceData *)PE_LDD_GetDeviceStructure(PE_LDD_COMPONENT_BitIoLdd13_ID))
#elif Arduino
//todo Agregar librerias necesareias de arduino IDE
#else
#endif




// Funciones a abtraer
void NEO_Delay_ms(uint32_t ms);

void NEO_GPIO_Read(GPIO_TypeDef *Port, uint16_t Pin, uint8_t *state);
void NEO_GPIO_Write(GPIO_TypeDef *Port, uint16_t Pin, uint8_t state);
void NEO_GPIO_Toggle(GPIO_TypeDef *Port, uint16_t Pin);

#endif /* ST_UNITTEST_CORE_INC_NEO_CONFIG_UC_H_ */
