/*
 * NEO_Config_uC.c
 *
 *  Created on: 27 jul 2026
 *      Author: Ruben Valdez
 */
#include "NEO_Config_uC.h"


#ifdef STM32

void NEO_Delay_ms(uint32_t ms){
	HAL_Delay(ms);
}

void NEO_GPIO_Read(GPIO_TypeDef *Port, uint16_t Pin, uint8_t *state){
	*state = HAL_GPIO_ReadPin(Port, Pin);
}
void NEO_GPIO_Write(GPIO_TypeDef *Port, uint16_t Pin, uint8_t state){
	if (state) {HAL_GPIO_WritePin(Port, Pin, GPIO_PIN_SET);}
	else {HAL_GPIO_WritePin(Port, Pin, GPIO_PIN_RESET);}
}
void NEO_GPIO_Toggle(GPIO_TypeDef *Port, uint16_t Pin){
	HAL_GPIO_TogglePin(Port, Pin);
}

uint8_t NEO_I2C_Transmit(I2C_HandleTypeDef *i2c_s, uint16_t Address, uint8_t *pDatos, uint16_t CantDatos){
	uint8_t status = HAL_I2C_Master_Transmit(i2c_s, Address, pDatos, CantDatos, I2C_A_TIMOUT);
	return status;
}
uint8_t NEO_I2C_Receive (I2C_HandleTypeDef *i2c_s, uint16_t Address, uint8_t *pDatos, uint16_t CantDatos){
	uint8_t status = HAL_I2C_Master_Receive(i2c_s, Address, pDatos, CantDatos, I2C_A_TIMOUT);
	return status;
}

#elif NXP

void NEO_Delay_ms(uint32_t ms){
	WAIT1_Waitms(ms);	//Por ejemplo en CodeWarrior, se asignaria esta funcion
}
void NEO_GPIO_Read(GPIO_TypeDef *Port, uint16_t Pin, uint8_t *state){
	switch (Pin) {
		case 13:
			*state = BitIoLdd13_GetVal(LDD_TDeviceData *DeviceDataPtr);
			break;
		default:
			break;
	}

}
void NEO_GPIO_Write(GPIO_TypeDef *Port, uint16_t Pin, uint8_t state){
	switch (Pin) {
		case 13:
			BitIoLdd13_PutVal(BitIoLdd13_DeviceData, (state));
			break;
		default:
			break;
	}
}
void NEO_GPIO_Toggle(GPIO_TypeDef *Port, uint16_t Pin){
	switch (Pin) {
		case 13:
			if(BitIoLdd13_GetVal(LDD_TDeviceData *DeviceDataPtr)){BitIoLdd13_PutVal(BitIoLdd13_DeviceData, (0));}
			else{BitIoLdd13_PutVal(BitIoLdd13_DeviceData, (1));}
			break;
		default:
			break;
	}
}

#elif Arduino

void NEO_Delay_ms(uint32_t ms){
	delay(ms);		//Por ejemplo en Arduino IDE, se asignaria esta funcion
}

void NEO_GPIO_Read(GPIO_TypeDef *Port, uint16_t Pin, uint8_t *state){
	*state = digitalRead(Pin);
}
void NEO_GPIO_Write(GPIO_TypeDef *Port, uint16_t Pin, uint8_t state){
	if (state) {digitalWrite(Pin, HIGH);}
	else {digitalWrite(Pin, LOW);}
}
void NEO_GPIO_Toggle(GPIO_TypeDef *Port, uint16_t Pin){
	if (digitalRead(Pin)) {digitalWrite(Pin, LOW);}
	else {digitalWrite(Pin, HIGH);}
}
#else

#endif
