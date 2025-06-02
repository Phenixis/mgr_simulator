
# PLC Configuration for Bottle Filling Station Simulation

## PLC Configuration

TIA Portal V15.1
PLCSIM S7-1500

CPU 1511-1 PN
Version: 2.5

## Values

INPUTS = values modified by the PLC
OUTPUTS = values taken by the PLC to modify the INPUTS
MEMORY = values stored in the PLC memory for state management

```
INPUTS = [
      0.0 => production_line_run (BOOL)
      0.1 => machineA_redLight (BOOL)
      0.2 => machineA_orangeLight (BOOL)
      0.3 => machineA_greenLight (BOOL)
      0.4 => machineB_redLight (BOOL)
      0.5 => machineB_orangeLight (BOOL)
      0.6 => machineB_greenLight (BOOL)
      0.7 => machineC_redLight (BOOL)

      1.0 => machineC_orangeLight (BOOL)
      1.1 => machineC_greenLight (BOOL)
      1.2 => machineA_topRedLight (BOOL)
      1.3 => machineA_topOrangeLight (BOOL)
      1.4 => machineA_topGreenLight (BOOL)
      1.5 => machineB_topRedLight (BOOL)
      1.6 => machineB_topOrangeLight (BOOL)
      1.7 => machineB_topGreenLight (BOOL)

      2.0 => machineC_topRedLight (BOOL)
      2.1 => machineC_topOrangeLight (BOOL)
      2.2 => machineC_topGreenLight (BOOL)
      2.3 => machineA_goDown (BOOL)
      2.4 => machineA_goUp (BOOL)
      2.5 => machineA_toolOn (BOOL)
      2.6 => machineA_toolOff (BOOL)
      2.7 => machineA_ack (BOOL)
      
      3.0 => machineA_unknown (BOOL)
      3.1 => machineB_goDown (BOOL)
      3.2 => machineB_goUp (BOOL)
      3.3 => machineB_toolOn (BOOL)
      3.4 => machineB_toolOff (BOOL)
      3.5 => machineB_ack (BOOL)
      3.6 => machineB_unknown (BOOL)
      3.7 => machineC_goDown (BOOL)
      
      4.0 => machineC_goUp (BOOL)
      4.1 => machineC_toolOn (BOOL)
      4.2 => machineC_toolOff (BOOL)
      4.3 => machineC_ack (BOOL)
      4.4 => machineC_unknown (BOOL)
]

OUTPUTS = [
      5.0 => machineA_leftSensor (BOOL)
      5.1 => machineA_rightSensor (BOOL)
      5.2 => machineB_leftSensor (BOOL)
      5.3 => machineB_rightSensor (BOOL)
      5.4 => machineC_leftSensor (BOOL)
      5.5 => machineC_rightSensor (BOOL)
      5.6 => machineA_startPos (BOOL)
      5.7 => machineA_endPos (BOOL)

      6.0 => machineA_toolWork (BOOL)
      6.1 => machineA_toolReady (BOOL)
      6.2 => machineA_error (BOOL)
      6.3 => machineB_startPos (BOOL)
      6.4 => machineB_endPos (BOOL)
      6.5 => machineB_toolWork (BOOL)
      6.6 => machineB_toolReady (BOOL)
      6.7 => machineB_error (BOOL)

      7.0 => machineC_startPos (BOOL)
      7.1 => machineC_endPos (BOOL)
      7.2 => machineC_toolWork (BOOL)
      7.3 => machineC_toolReady (BOOL)
      7.4 => machineC_error (BOOL)
]

MEMORY = [
      8.0 => _machineA_hasBottle (BOOL)
      8.1 => _machineA_working (BOOL)
      8.2 => _machineA_operation_done (BOOL)
      8.3 => _machineB_hasBottle (BOOL)
      8.4 => _machineB_working (BOOL)
      8.5 => _machineB_operation_done (BOOL)
      8.6 => _machineC_hasBottle (BOOL)
      8.7 => _machineC_working (BOOL)

      9.0 => _machineC_operation_done (BOOL)
]
```

## NETWORKS

### NETWORK 1 - Production Line Run

```
|--[/]_machineA_working--[/]_machineB_working--[/]_machineC_working---------------------------------------------------------------------( )production_line_run--|
```

### NETWORK 2 - Machine A stops production line when bottle

```
|--[ ]machineA_leftSensor--[ ]machineA_rightSensor-----------------------------------------------------------------------------------------------------------( )_machineA_hasBottle--|
// If left sensor and right sensor are both triggered, then the machine has a bottle

|--[/]_machineA_operation_done--[ ]machineA_startPos--[ ]machineA_leftSensor--[ ]machineA_rightSensor--------------------------------------------------------(S)_machineA_working--|
// If the operation is not done, the machine is still at its starting position and the sensors are triggered, it starts working

|--[ ]_machineA_operation_done--[ ]machineA_startPos--[ ]machineA_leftSensor--[ ]machineA_rightSensor--------------------------------------------------------(R)_machineA_working--|
// If the operation is done, the machine is at its starting position and the sensors are triggered, it stops working
```

### NETWORK 3 - Machine A lights
```
|--[/]machineA_error--[ ]_machineA_hasBottle---------------------------------------------------------------------------------------------------( )machineA_topOrangeLight--|
// If there is no error and the machine has a bottle, the top orange light is on

|--[/]machineA_error--[/]_machineA_hasBottle---------------------------------------------------------------------------------------------------( )machineA_topGreenLight--|
// If there is no error and the machine does not have a bottle, the top green light is on

|--[ ]machineA_error---------------------------------------------------------------------------------------------------------------------------( )machineA_topRedLight--|
// If there is an error, the top red light is on

|--[ ]machineA_leftSensor--[/]machineA_rightSensor--+------------------------------------------------------------------------------------------( )machineA_orangeLight--|
                                                    |
|--[/]machineA_leftSensor--[ ]machineA_rightSensor--+
// If one of the sensors is triggered, the orange light is on

|--[/]machineA_leftSensor--[/]machineA_rightSensor---------------------------------------------------------------------------------------------( )machineA_redLight--|
// If both sensors are not triggered, the red light is on

|--[ ]machineA_leftSensor--[ ]machineA_rightSensor---------------------------------------------------------------------------------------------( )machineA_greenLight--|
// If both sensors are triggered, the green light is on
```

### NETWORK 4 - Machine A tool

```
|--[/]_machineA_operation_done--[ ]_machineA_hasBottle--[/]machineA_endPos---------------------------------------------------------------------( )machineA_goDown--|
// If the operation is not done, the machine has a bottle and is not at its end position, it goes down

|--[/]_machineA_operation_done--[ ]_machineA_hasBottle--[ ]machineA_endPos--[/]machineA_goDown--[/]machineA_toolOff----------------------------( )machineA_toolOn--|
// If the operation is not done, the machine has a bottle, is at its end position, is not going down, and the tool is off, it turns the tool on

                                                                                                |  TON  |
|--[/]_machineA_operation_done--[ ]_machineA_hasBottle--[ ]machineA_endPos--[ ]machineA_toolOn--|IN----Q|--------------------------------------(S)_machineA_operation_done--|
                                                                                       T#250ms--|PT   ET|--
// If the operation is not done, the machine has a bottle, is at its end position, and the tool is on, it waits for 250ms before marking the operation as done

|--[ ]_machineA_operation_done--[ ]_machineA_hasBottle--[ ]machineA_endPos--[/]machineA_goUp--[/]machineA_toolOn-------------------------------( )machineA_toolOff--|
// If the operation is done, the machine has a bottle, is at its end position, is not going up, and the tool is not on, it turns the tool off.

|--[ ]_machineA_operation_done--[ ]_machineA_hasBottle--[/]machineA_toolWork-------------------------------------------------------------------( )machineA_goUp--|
// If the operation is done, the machine has a bottle, and the tool is not working, it goes up

|--[ ]_machineA_operation_done--[ ]machineA_leftSensor--[/]machineA_rightSensor--[ ]machineA_startPos------------------------------------------(R)_machineA_operation_done--|
// If the operation is done, the left sensor is triggered, the right sensor is not triggered, and the machine is at its starting position, it resets the operation done flag
```

### NETWORK 5 - Machine B stops production line when bottle

```
|--[ ]machineB_leftSensor--[ ]machineB_rightSensor-----------------------------------------------------------------------------------------------------------( )_machineB_hasBottle--|
// If left sensor and right sensor are both triggered, then the machine has a bottle

|--[/]_machineB_operation_done--[ ]machineB_startPos--[ ]machineB_leftSensor--[ ]machineB_rightSensor--------------------------------------------------------(S)_machineB_working--|
// If the operation is not done, the machine is still at its starting position and the sensors are triggered, it starts working

|--[ ]_machineB_operation_done--[ ]machineB_startPos--[ ]machineB_leftSensor--[ ]machineB_rightSensor--------------------------------------------------------(R)_machineB_working--|
// If the operation is done, the machine is at its starting position and the sensors are triggered, it stops working
```

### NETWORK 6 - Machine B lights
```
|--[/]machineB_error--[ ]_machineB_hasBottle---------------------------------------------------------------------------------------------------( )machineB_topOrangeLight--|
// If there is no error and the machine has a bottle, the top orange light is on

|--[/]machineB_error--[/]_machineB_hasBottle---------------------------------------------------------------------------------------------------( )machineB_topGreenLight--|
// If there is no error and the machine does not have a bottle, the top green light is on

|--[ ]machineB_error---------------------------------------------------------------------------------------------------------------------------( )machineB_topRedLight--|
// If there is an error, the top red light is on

|--[ ]machineB_leftSensor--[/]machineB_rightSensor--+------------------------------------------------------------------------------------------( )machineB_orangeLight--|
                                                    |
|--[/]machineB_leftSensor--[ ]machineB_rightSensor--+
// If one of the sensors is triggered, the orange light is on

|--[/]machineB_leftSensor--[/]machineB_rightSensor---------------------------------------------------------------------------------------------( )machineB_redLight--|
// If both sensors are not triggered, the red light is on

|--[ ]machineB_leftSensor--[ ]machineB_rightSensor---------------------------------------------------------------------------------------------( )machineB_greenLight--|
// If both sensors are triggered, the green light is on
```

### NETWORK 7 - Machine B tool

```
|--[/]_machineB_operation_done--[ ]_machineB_hasBottle--[/]machineB_endPos---------------------------------------------------------------------( )machineB_goDown--|
// If the operation is not done, the machine has a bottle and is not at its end position, it goes down

|--[/]_machineB_operation_done--[ ]_machineB_hasBottle--[ ]machineB_endPos--[/]machineB_goDown--[/]machineB_toolOff----------------------------( )machineB_toolOn--|
// If the operation is not done, the machine has a bottle, is at its end position, is not going down, and the tool is off, it turns the tool on

                                                                                                |  TON  |
|--[/]_machineB_operation_done--[ ]_machineB_hasBottle--[ ]machineB_endPos--[ ]machineB_toolOn--|IN----Q|--------------------------------------(S)_machineB_operation_done--|
                                                                                       T#750ms--|PT   ET|--
// If the operation is not done, the machine has a bottle, is at its end position, and the tool is on, it waits for 750ms before marking the operation as done

|--[ ]_machineB_operation_done--[ ]_machineB_hasBottle--[ ]machineB_endPos--[/]machineB_goUp--[/]machineB_toolOn-------------------------------( )machineB_toolOff--|
// If the operation is done, the machine has a bottle, is at its end position, is not going up, and the tool is not on, it turns the tool off.

|--[ ]_machineB_operation_done--[ ]_machineB_hasBottle--[/]machineB_toolWork-------------------------------------------------------------------( )machineB_goUp--|
// If the operation is done, the machine has a bottle, and the tool is not working, it goes up

|--[ ]_machineB_operation_done--[ ]machineB_leftSensor--[/]machineB_rightSensor--[ ]machineB_startPos------------------------------------------(R)_machineB_operation_done--|
// If the operation is done, the left sensor is triggered, the right sensor is not triggered, and the machine is at its starting position, it resets the operation done flag
```

### NETWORK 8 - Machine C stops production line when bottle

```
|--[ ]machineC_leftSensor--[ ]machineC_rightSensor-----------------------------------------------------------------------------------------------------------( )_machineC_hasBottle--|
// If left sensor and right sensor are both triggered, then the machine has a bottle

|--[/]_machineC_operation_done--[ ]machineC_startPos--[ ]machineC_leftSensor--[ ]machineC_rightSensor--------------------------------------------------------(S)_machineC_working--|
// If the operation is not done, the machine is still at its starting position and the sensors are triggered, it starts working

|--[ ]_machineC_operation_done--[ ]machineC_startPos--[ ]machineC_leftSensor--[ ]machineC_rightSensor--------------------------------------------------------(R)_machineC_working--|
// If the operation is done, the machine is at its starting position and the sensors are triggered, it stops working
```

### NETWORK 9 - Machine C lights
```
|--[/]machineC_error--[ ]_machineC_hasBottle---------------------------------------------------------------------------------------------------( )machineC_topOrangeLight--|
// If there is no error and the machine has a bottle, the top orange light is on

|--[/]machineC_error--[/]_machineC_hasBottle---------------------------------------------------------------------------------------------------( )machineC_topGreenLight--|
// If there is no error and the machine does not have a bottle, the top green light is on

|--[ ]machineC_error---------------------------------------------------------------------------------------------------------------------------( )machineC_topRedLight--|
// If there is an error, the top red light is on

|--[ ]machineC_leftSensor--[/]machineC_rightSensor--+------------------------------------------------------------------------------------------( )machineC_orangeLight--|
                                                    |
|--[/]machineC_leftSensor--[ ]machineC_rightSensor--+
// If one of the sensors is triggered, the orange light is on

|--[/]machineC_leftSensor--[/]machineC_rightSensor---------------------------------------------------------------------------------------------( )machineC_redLight--|
// If both sensors are not triggered, the red light is on

|--[ ]machineC_leftSensor--[ ]machineC_rightSensor---------------------------------------------------------------------------------------------( )machineC_greenLight--|
// If both sensors are triggered, the green light is on
```

### NETWORK 10 - Machine C tool

```
|--[/]_machineC_operation_done--[ ]_machineC_hasBottle--[/]machineC_endPos---------------------------------------------------------------------( )machineC_goDown--|
// If the operation is not done, the machine has a bottle and is not at its end position, it goes down

|--[/]_machineC_operation_done--[ ]_machineC_hasBottle--[ ]machineC_endPos--[/]machineC_goDown--[/]machineC_toolOff----------------------------( )machineC_toolOn--|
// If the operation is not done, the machine has a bottle, is at its end position, is not going down, and the tool is off, it turns the tool on

                                                                                                |  TON  |
|--[/]_machineC_operation_done--[ ]_machineC_hasBottle--[ ]machineC_endPos--[ ]machineC_toolOn--|IN----Q|--------------------------------------(S)_machineC_operation_done--|
                                                                                       T#600ms--|PT   ET|--
// If the operation is not done, the machine has a bottle, is at its end position, and the tool is on, it waits for 600ms before marking the operation as done

|--[ ]_machineC_operation_done--[ ]_machineC_hasBottle--[ ]machineC_endPos--[/]machineC_goUp--[/]machineC_toolOn-------------------------------( )machineC_toolOff--|
// If the operation is done, the machine has a bottle, is at its end position, is not going up, and the tool is not on, it turns the tool off.

|--[ ]_machineC_operation_done--[ ]_machineC_hasBottle--[/]machineC_toolWork-------------------------------------------------------------------( )machineC_goUp--|
// If the operation is done, the machine has a bottle, and the tool is not working, it goes up

|--[ ]_machineC_operation_done--[ ]machineC_leftSensor--[/]machineC_rightSensor--[ ]machineC_startPos------------------------------------------(R)_machineC_operation_done--|
// If the operation is done, the left sensor is triggered, the right sensor is not triggered, and the machine is at its starting position, it resets the operation done flag
```