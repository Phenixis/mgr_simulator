
# PLC Configuration for Bottle Filling Station Simulation

## PLC Configuration

TIA Portal V15.1
PLCSIM S7-1500

CPU 1511-1 PN
Version: 2.5

## Values

The PLC program is designed to control a bottle filling station with three machines (A, B, and C). Each machine has various sensors and lights to indicate its status. The program uses inputs, outputs, and memory to manage the state of the machines and the production line. These values should be configured in the PLC "Default tag table" in the PLC Tags section. The memory addresses are important because the simulation will read and write values from these addresses.

INPUTS = values modified by the PLC (read by the simulation to acknowledge a modification)
OUTPUTS = values used by the PLC to modify the INPUTS (written by the simulation to signal a modification to the PLC)
MEMORY = values stored in the PLC memory for state management

```
INPUTS = [
      M0.0 => production_line_run (BOOL)
      M0.1 => machineA_redLight (BOOL)
      M0.2 => machineA_orangeLight (BOOL)
      M0.3 => machineA_greenLight (BOOL)
      M0.4 => machineB_redLight (BOOL)
      M0.5 => machineB_orangeLight (BOOL)
      M0.6 => machineB_greenLight (BOOL)
      M0.7 => machineC_redLight (BOOL)

      M1.0 => machineC_orangeLight (BOOL)
      M1.1 => machineC_greenLight (BOOL)
      M1.2 => machineA_topRedLight (BOOL)
      M1.3 => machineA_topOrangeLight (BOOL)
      M1.4 => machineA_topGreenLight (BOOL)
      M1.5 => machineB_topRedLight (BOOL)
      M1.6 => machineB_topOrangeLight (BOOL)
      M1.7 => machineB_topGreenLight (BOOL)

      M2.0 => machineC_topRedLight (BOOL)
      M2.1 => machineC_topOrangeLight (BOOL)
      M2.2 => machineC_topGreenLight (BOOL)
      M2.3 => machineA_goDown (BOOL)
      M2.4 => machineA_goUp (BOOL)
      M2.5 => machineA_toolOn (BOOL)
      M2.6 => machineA_toolOff (BOOL)
      M2.7 => machineA_ack (BOOL)
      
      M3.0 => machineA_unknown (BOOL)
      M3.1 => machineB_goDown (BOOL)
      M3.2 => machineB_goUp (BOOL)
      M3.3 => machineB_toolOn (BOOL)
      M3.4 => machineB_toolOff (BOOL)
      M3.5 => machineB_ack (BOOL)
      M3.6 => machineB_unknown (BOOL)
      M3.7 => machineC_goDown (BOOL)
      
      M4.0 => machineC_goUp (BOOL)
      M4.1 => machineC_toolOn (BOOL)
      M4.2 => machineC_toolOff (BOOL)
      M4.3 => machineC_ack (BOOL)
      M4.4 => machineC_unknown (BOOL)
]

OUTPUTS = [
      M5.0 => machineA_leftSensor (BOOL)
      M5.1 => machineA_rightSensor (BOOL)
      M5.2 => machineB_leftSensor (BOOL)
      M5.3 => machineB_rightSensor (BOOL)
      M5.4 => machineC_leftSensor (BOOL)
      M5.5 => machineC_rightSensor (BOOL)
      M5.6 => machineA_startPos (BOOL)
      M5.7 => machineA_endPos (BOOL)

      M6.0 => machineA_toolWork (BOOL)
      M6.1 => machineA_toolReady (BOOL)
      M6.2 => machineA_error (BOOL)
      M6.3 => machineB_startPos (BOOL)
      M6.4 => machineB_endPos (BOOL)
      M6.5 => machineB_toolWork (BOOL)
      M6.6 => machineB_toolReady (BOOL)
      M6.7 => machineB_error (BOOL)

      M7.0 => machineC_startPos (BOOL)
      M7.1 => machineC_endPos (BOOL)
      M7.2 => machineC_toolWork (BOOL)
      M7.3 => machineC_toolReady (BOOL)
      M7.4 => machineC_error (BOOL)
]

MEMORY = [
      M8.0 => _machineA_hasBottle (BOOL)
      M8.1 => _machineA_working (BOOL)
      M8.2 => _machineA_operation_done (BOOL)
      M8.3 => _machineB_hasBottle (BOOL)
      M8.4 => _machineB_working (BOOL)
      M8.5 => _machineB_operation_done (BOOL)
      M8.6 => _machineC_hasBottle (BOOL)
      M8.7 => _machineC_working (BOOL)

      M9.0 => _machineC_operation_done (BOOL)
]
```

## NETWORKS

The networks are ladder logic diagrams that should be configured in the Main [OB1] block of the PLC program. They used the LAD programming language, here is a brief explanation on how it works:

- A network contains multiple rungs.
- A rung is a horizontal line that represents a logical operation.
- Each rung consists of conditions on the left side and an output on the right side.
- The left side of the rung contains the conditions that must be met for the output on the right side to be activated.
- The conditions are represented by contacts, which can be normally open (represented by `[ ]`) or normally closed (represented by `[/]`).
- A normally open contact (`[ ]`) is triggered when the associated input or memory bit is true (ON). It means that when the input or memory bit is true, the contact allows current to pass through.
- A normally closed contact (`[/]`) is triggered when the associated input or memory bit is false (OFF). It means that when the input or memory bit is false, the contact allows current to pass through.
- There are also special contacts like `TON` (Timer On Delay) which are used to create time delays in the logic. They are represented by `|  TON  |` and have inputs like `IN` and `PT` (Preset Time) and outputs like `Q` (Output) and `ET` (Elapsed Time). `PT` is the time duration for which the timer will run before activating the output `Q`.
- The output is represented by a coil, which is activated when the conditions on the left side are met. The coil is represented by `( )` followed by the name of the output or memory bit.
- If the coil is open (`( )`), it means that the output will be activated when the conditions are met.
- If the coil is set (`(S)`), it means that the output will be set to true when the conditions are met and will remain true until it is reset.
- If the coil is reset (`(R)`), it means that the output will be set to false when the conditions are met and will remain false until it is set again.

### NETWORK 1 - Production Line Run

```
|--[/]_machineA_working--[/]_machineB_working--[/]_machineC_working---------------------------------------------------------------------( )production_line_run--|
// If none of the machines are working, the production line is running
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