
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

      3.0 => machineB_goDown (BOOL)
      3.1 => machineB_goUp (BOOL)
      3.2 => machineB_toolOn (BOOL)
      3.3 => machineB_toolOff (BOOL)
      3.4 => machineB_ack (BOOL)
      3.5 => machineC_goDown (BOOL)
      3.6 => machineC_goUp (BOOL)
      3.7 => machineC_toolOn (BOOL)

      4.0 => machineC_toolOff (BOOL)
      4.1 => machineC_ack (BOOL)
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
      10.0: _openA (BOOL)
      10.1: _openA_reset (BOOL)
      10.2: _A_ok (BOOL)
      10.3: _A_end_pos (BOOL)
      10.4: _last_A_rightSensor (BOOL)
      10.5: _last_A_leftSensor (BOOL)
      10.6: _openB (BOOL)
      10.7: _openB_reset (BOOL)

      11.0: _B_ok (BOOL)
      11.1: _B_end_pos (BOOL)
      11.2: _last_B_rightSensor (BOOL)
      11.3: _last_B_leftSensor (BOOL)
      11.4: _openC (BOOL)
      11.5: _openC_reset (BOOL)
      11.6: _C_ok (BOOL)
      11.7: _C_end_pos (BOOL)

      12.0: _last_C_rightSensor (BOOL)
      12.1: _last_C_leftSensor (BOOL)

      13.0: _A_to_B_queue (WORD)

      16.0: _B_to_C_queue (WORD)
]
```

## NETWORKS

### NETWORK 1 - Production Line Run condition

```
|--[/]machineA_topOrangeLight--[/]machineB_topOrangeLight--[/]machineC_topOrangeLight---------------------------------------------------------------------(S)production_line_run--|
```

### NETWORK 2 - Machine A Sensor Lights

```
|--[/]machineA_leftSensor--[/]machineA_rightSensor-----------------------------------------------------------------------------------------------------------( )machineA_redLight--|

|--[ ]machineA_leftSensor--[/]machineA_rightSensor--+--------------------------------------------------------------------------------------------------------( )machineA_orangeLight--|
                                                    |
|--[/]machineA_leftSensor--[ ]machineA_rightSensor--+

|--[ ]machineA_leftSensor--[ ]machineA_rightSensor-----------------------------------------------------------------------------------------------------------( )machineA_greenLight--|
```

### NETWORK 3 - Machine B Sensor Lights
```
|--[/]machineB_leftSensor--[/]machineB_rightSensor-----------------------------------------------------------------------------------------------------------( )machineB_redLight--|

|--[ ]machineB_leftSensor--[/]machineB_rightSensor--+--------------------------------------------------------------------------------------------------------( )machineB_orangeLight--|
                                                    |
|--[ ]machineB_rightSensor--[/]machineB_leftSensor--+

|--[ ]machineB_leftSensor--[ ]machineB_rightSensor-----------------------------------------------------------------------------------------------------------( )machineB_greenLight--|
```

### NETWORK 4 - Machine C Sensor Lights

```
|--[/]machineC_leftSensor--[/]machineC_rightSensor-----------------------------------------------------------------------------------------------------------( )machineC_redLight--|

|--[ ]machineC_leftSensor--[/]machineC_rightSensor--+--------------------------------------------------------------------------------------------------------( )machineC_orangeLight--|
                                                    |
|--[ ]machineC_rightSensor--[/]machineC_leftSensor--+

|--[ ]machineC_leftSensor--[ ]machineC_rightSensor-----------------------------------------------------------------------------------------------------------( )machineC_greenLight--|
```

### NETWORK 5 - Machine A Operation Start

```
|--[ ]machineA_leftSensor--[ ]machineA_rightSensor--[ ]_openA--+----------------------------------------------------------------------( )machineA_ack--|
                                                               |
                                                               +---------------------------------------------------------------------------------------------(S)_openA_reset--|
                                                               |
                                                               +---------------------------------------------------------------------------------------------(R)production_line_run--|
                                                               |
                                                               +---------------------------------------------------------------------------------------------(S)machineA_topOrangeLight--|
```

### NETWORK 6 - Machine B Operation Start

```
|--[ ]machineB_leftSensor--[ ]machineB_rightSensor--[ ]_openB--[        CALL FC_GetQueueBit        ]--[ ]FC_GetQueueBit_DB.Value--+--( )machineB_ack--|
                                                               |  Parameters:                      |                              |
                                                               |  Queue: _A_to_B_queue             |                              |
                                                               |  Position: 0                      |                              |
                                                               |  Value: FC_GetQueueBit_DB.Value   |                              |
                                                               // You save the value where it already is to use it just after     |
                                                                                                                                  +---(S)_openB_reset--|
                                                                                                                                  |
                                                                                                                                  +---(R)production_line_run--|
                                                                                                                                  |
                                                                                                                                  +---(S)machineB_topOrangeLight--|
```

### NETWORK 7 - Machine C Operation Start

```
|--[ ]machineC_leftSensor--[ ]machineC_rightSensor--[ ]_openC--[        CALL FC_GetQueueBit        ]--[ ]FC_GetQueueBit_DB.Value--+--( )machineC_ack--|
                                                               |  Parameters:                      |                              |
                                                               |  Queue: _B_to_C_queue             |                              |
                                                               |  Position: 0                      |                              |
                                                               |  Value: FC_GetQueueBit_DB.Value   |                              |
                                                                                                                                  +---(S)_openC_reset--|
                                                                                                                                  |
                                                                                                                                  +---(R)production_line_run--|
                                                                                                                                  |
                                                                                                                                  +---(S)machineC_topOrangeLight--|
```

### NETWORK 8 - Machine A Quality Status

```
|--[/]_openA--+--[ ]machineA_toolReady-----------------------------------------------------------------------------------------------------------------------(S)_A_ok--|
              |
              +--[ ]machineA_error---------------------------------------------------------------------------------------------------------------------------(R)_A_ok--|

|--[ ]machineA_startPos--[ ]_A_end_pos--+--------------------------------------------------------------------------------------------------------------------(/)machineA_topOrangeLight--|
                                        |
                                        +--[ ]_A_ok--+-------------------------------------------------------------------------------------------------------(/)machineA_topRedLight--|
                                        |            |
                                        |            +-------------------------------------------------------------------------------------------------------( )machineA_topGreenLight--|
                                        |
                                        +--[/]_A_ok--+-------------------------------------------------------------------------------------------------------( )machineA_topRedLight--|
                                                     |
                                                     +-------------------------------------------------------------------------------------------------------(/)machineA_topGreenLight--|
```

### NETWORK 9 - Machine B Quality Status

```
|--[/]_openB--+--[ ]machineB_toolReady-----------------------------------------------------------------------------------------------------------------------(S)_B_ok--|
              |
              +--[ ]machineB_error---------------------------------------------------------------------------------------------------------------------------(R)_B_ok--|

|--[ ]machineB_startPos--[ ]_B_end_pos--+--------------------------------------------------------------------------------------------------------------------(/)machineB_topOrangeLight--|
                                        |
                                        +--[ ]_B_ok--+-------------------------------------------------------------------------------------------------------(/)machineB_topRedLight--|
                                        |            |
                                        |            +-------------------------------------------------------------------------------------------------------( )machineB_topGreenLight--|
                                        |
                                        +--[/]_B_ok--+-------------------------------------------------------------------------------------------------------( )machineB_topRedLight--|
                                                     |
                                                     +-------------------------------------------------------------------------------------------------------(/)machineB_topGreenLight--|
```

### NETWORK 10 - Machine C Quality Status

```
|--[/]_openC--+--[ ]machineC_toolReady-----------------------------------------------------------------------------------------------------------------------(S)_C_ok--|
              |
              +--[ ]machineC_error---------------------------------------------------------------------------------------------------------------------------(R)_C_ok--|

|--[ ]machineC_startPos--[ ]_C_end_pos--+--------------------------------------------------------------------------------------------------------------------(/)machineC_topOrangeLight--|
                                        |
                                        +--[ ]_C_ok--+-------------------------------------------------------------------------------------------------------(/)machineC_topRedLight--|
                                        |            |
                                        |            +-------------------------------------------------------------------------------------------------------( )machineC_topGreenLight--|
                                        |
                                        +--[/]_C_ok--+-------------------------------------------------------------------------------------------------------( )machineC_topRedLight--|
                                                     |
                                                     +-------------------------------------------------------------------------------------------------------(/)machineC_topGreenLight--|
```

### NETWORK 11 - Machine A to B Quality Queue

```
// Add quality result to queue when part leaves Machine A
|--[ ]_last_A_rightSensor--[/]machineA_rightSensor--[/]_openA--+--[ ]_A_ok-----------------------------------------------------------------------------------[   CALL FC_AddToQueue   ]--|
                                                               |                                                                                             |  Input parameters:     |
                                                               |                                                                                             |  Queue: _A_to_B_queue  |
                                                               |                                                                                             |  Value: 1 (good part)  |
                                                               |
                                                               +--[/]_A_ok-----------------------------------------------------------------------------------[   CALL FC_AddToQueue   ]--|
                                                               |                                                                                             |  Input parameters:     |
                                                               |                                                                                             |  Queue: _A_to_B_queue  |
                                                               |                                                                                             |  Value: 0 (bad part)   |
                                                               |
                                                               +----------------------(S)_openA--|
```

### NETWORK 12 - Machine B to C Quality Queue

```
// Add quality result to queue when part leaves Machine B
|--[ ]_last_B_rightSensor--[/]machineB_rightSensor--[/]_openB--+--[ ]_B_ok-----------------------------------------------------------------------------------[   CALL FC_AddToQueue   ]--|
                                                               |                                                                                             |  Input parameters:     |
                                                               |                                                                                             |  Queue: _B_to_C_queue  |
                                                               |                                                                                             |  Value: 1 (good part)  |
                                                               |
                                                               +--[/]_B_ok-----------------------------------------------------------------------------------[   CALL FC_AddToQueue   ]--|
                                                                                                                                                             |  Input parameters:     |
                                                                                                                                                             |  Queue: _B_to_C_queue  |
                                                                                                                                                             |  Value: 0 (bad part)   |

// Shift A to B queue when part enters Machine B
|--[/]machineB_rightSensor--[ ]_last_B_rightSensor-----------------------------------------------------------------------------------------------------------[  CALL FC_ShiftQueue   ]--|
                                                                                                                                                             | Input parameter:      |
                                                                                                                                                             | Queue: _A_to_B_queue  |

// Shift B to C queue when part enters Machine C
|--[/]machineC_rightSensor--[ ]_last_C_rightSensor--+--------------------------------------------------------------------------------------------------------[  CALL FC_ShiftQueue   ]--|
                                                    |                                                                                                        | Input parameter:      |
                                                    |                                                                                                        | Queue: _B_to_C_queue  |
                                                    |
                                                    +--[/]_openC---------------------------------------------------------------------------------------------(S)_openC--|
```

### NETWORK 13 - Edge Detection Memory

```
|--[ ]machineA_leftSensor------------------------------------------------------------------------------------------------------------------------------------( )_last_A_leftSensor--|

|--[ ]machineA_rightSensor-----------------------------------------------------------------------------------------------------------------------------------( )_last_A_rightSensor--|

|--[ ]machineB_leftSensor------------------------------------------------------------------------------------------------------------------------------------( )_last_B_leftSensor--|

|--[ ]machineB_rightSensor-----------------------------------------------------------------------------------------------------------------------------------( )_last_B_rightSensor--|

|--[ ]machineC_leftSensor------------------------------------------------------------------------------------------------------------------------------------( )_last_C_leftSensor--|

|--[ ]machineC_rightSensor-----------------------------------------------------------------------------------------------------------------------------------( )_last_C_rightSensor--|
```

## Function Blocks

### FC_AddToQueue

#### Input Parameters:

Queue (IN_OUT WORD) - The queue to modify
Value (IN BOOL) - Value to add (1 for good, 0 for bad)

#### STL Code:
```stl
      L     #Queue           // Load current Queue
      SLW   1                // Shift left
      T     #Queue           // Store back

      A     #Value           // If #Value is TRUE
      JCN   skipOR           // Skip if not true

      L     #Queue           // Load Queue
      L     W#16#0001        // Load constant
      O                     // OR operation (word)
      T     #Queue           // Store back

skipOR: NOP   0
```

### FC_ShiftQueue

#### Input Parameters:

Queue (IN_OUT WORD) - The queue to shift

#### STL Code:
```stl
      L     #Queue      // Load Queue
      SRW   1           // Shift Right Word by 1
      T     #Queue      // Store back into Queue
```

### FC_GetQueueBit

#### Input Parameters:

Queue (IN WORD) - The queue to read from
Position (IN INT) - Bit position (0 = rightmost)

#### Output Parameters:

Value (OUT BOOL) - The bit value

#### STL Code:
```stl
      L     1
      L     #Position          // bit index (0..15)
      SLW                     // 1 << Position → creates bitmask
      L     #Queue
      AW                      // Queue AND bitmask
      L     0
      <>I                     // Compare result ≠ 0
      =     #Value            // Store result in BOOL
```
