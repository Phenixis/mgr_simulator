# Simulator of filling bottles station controllable via PLC
This project is part of the completed diploma thesis.

Programing language: Python

Additional used software: PyGame, Snap7

## Installation and Setup

Follow these steps to get the project up and running:

1. **Clone the repository**  
   Run: `git clone https://github.com/Phenixis/mgr_simulation` and navigate to the project folder.

2. **Install Python 3.11.9**  
   We recommend using [pyenv](https://github.com/pyenv/pyenv) to manage Python versions on your system.

3. **Install pyenv**  
   Follow the instructions at the [pyenv-win repo](https://github.com/pyenv-win/pyenv-win) to set it up on Windows.

4. **Set up a virtual environment with Python 3.11.9**  
   Use these commands in your terminal or CMD:  
   - Install Python 3.11.9 with pyenv if needed:  
     `pyenv install 3.11.9`  
   - Set the local Python version:  
     `pyenv local 3.11.9`  
   - Create a virtual environment explicitly using pyenv’s Python:  
     `C:\Users\<username>\.pyenv\pyenv-win\versions\3.11.9\python.exe -m venv venv`  
   - Activate the virtual environment:  
     `venv\Scripts\activate.bat`

5. **Install dependencies**  
   Run: `pip install -r requirements.txt`

6. **Build the executable**  
   Run:  
      ```
      pyinstaller --onefile main.py --add-data "venv\Lib\site-packages\snap7;.\snap7" --add-data "img/*;img"
      move dist\main.exe .\main.exe
      ```

7. **Run the application**  
Run: `main.exe`

---

And that’s it — you’re good to go!

### Commands summary
#### Installing git and pyenv
Run these commands in a PowerShell with Administrator rights.
```
# Run PowerShell as Administrator before running this script!

# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Refresh environment variables so choco is available immediately
$env:Path += ";$env:ALLUSERSPROFILE\chocolatey\bin"

# Install Git
choco install git -y

$env:Path += ";${env:ProgramFiles}\Git\cmd"

# Install pyenv-win
git clone https://github.com/pyenv-win/pyenv-win.git "$HOME/.pyenv"

# Restart your PowerShell session or run these to refresh your environment variables
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims", [EnvironmentVariableTarget]::User)
```

#### Running the project
Run these commands in the command line.
```
cd %USERPROFILE%\Documents
git clone https://github.com/Phenixis/mgr_simulator
cd mgr_simulator

pyenv install 3.11.9
pyenv local 3.11.9

%USERPROFILE%\.pyenv\pyenv-win\versions\3.11.9\python.exe -m venv venv
venv\Scripts\activate.bat

pip install -r requirements.txt

pyinstaller --onefile main.py --add-data "venv\Lib\site-packages\snap7;.\snap7" --add-data "img/*;img"
move dist\main.exe .\main.exe

main.exe
```

If you made modifications and need to recompile the project, execute only these lines:
```
venv\Scripts\activate.bat

pyinstaller --onefile main.py --add-data "venv\Lib\site-packages\snap7;.\snap7" --add-data "img/*;img"
move dist\main.exe .\main.exe

main.exe
```

## Application description 
Prepared simulation shows a glass bottle filling station using 3 main operations. During the simulation, successive bottles appear on the production line, which transports them between three machines carrying out the following operations: bottle quality control, bottle filling and bottle closing. The prepared simulation enables the occurrence of many emergency situations, resulting, for example, from the appearance of a broken bottle, the correct operation of which belongs to the PLC program controlling the course of the simulated object. The prepared controller application has the ability to connect via Ethernet, both with the real PLC controller and the simulator of such a controller. In addition, the application gives the opportunity to perform simple operations in the simulation, allowing to assess the correctness of the application and enabling gradual implementation in the laboratory.

### PLC Connection Requirements
**Important**: This simulator requires a connection to a PLC to operate. The simulator will not function without a valid PLC connection.

#### Supported PLC Options:
1. **Real Siemens PLC**: Connect to an actual S7 PLC device on the network.
2. **PLC Simulator**: Use software like PLCSIM, S7-PLCSIM Advanced, or other S7 protocol compatible simulators.

#### PLC Configuration:
Edit the `simulator.ini` file to configure your PLC connection:
```ini
[plc]
address = 192.168.45.2  # IP address of your PLC or PLC simulator
rack = 0                # Rack number (typically 0)
slot = 1                # Slot number (typically 1 for CPU)
port = 102              # Communication port (default is 102 for S7 protocol)
```

## Application functionality
- simulation of filling bottles station realized in PyGame;
- controlling simulator behavior via computer keyboard;
- possibility to run simulation in self processing state;
- requires connection to a PLC device or PLC simulator via Snap7 library;
- possibility to control simulation from connected PLCs;
- automatic detection and connection to PLC using settings from simulator.ini;

## Screenshot of prepared application
![Alt text](./img/screenshot.jpg)
