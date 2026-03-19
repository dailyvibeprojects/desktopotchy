```text
===============================================================================
                       DESKTOPOTCHY USER DOCUMENTATION
                           VERSION 1.0.0 (C) 2026
===============================================================================

1. DESCRIPTION
-------------------------------------------------------------------------------
Desktopotchy is a background utility for monitoring user productivity via 
global hotkey interception. The entity evolves based on cumulative 
keystroke data (Bites and Pastes).

2. SYSTEM REQUIREMENTS
-------------------------------------------------------------------------------
* Operating System: Windows, macOS, or Linux
* Software: Python 3.x Environment
* Dependencies: pynput library

INSTALLATION:
C:\> pip install pynput

3. EXECUTION AND TERMINATION
-------------------------------------------------------------------------------
MANUAL START:
Navigate to the source directory and execute the following command:
C:\> python desktopotchy.py

MANUAL STOP:
Use the termination hotkey [CTRL+Q] (Windows/Linux) or [CMD+Q] (macOS).
Alternatively, break the process in the command line interface.

4. AUTOMATED STARTUP CONFIGURATION
-------------------------------------------------------------------------------
WINDOWS:
1. Execute [WIN+R] and enter "shell:startup"
2. Create New Shortcut
3. Target: pythonw.exe "C:\PATH\TO\desktopotchy.py"
   (pythonw.exe prevents the persistent console window)

MACOS:
1. Open Automator.app -> New Application
2. Add "Run Shell Script" action
3. Input: /usr/local/bin/python3 /PATH/TO/desktopotchy.py &
4. Save as Application and add to System Settings > Login Items

5. INTERACTION LOGIC
-------------------------------------------------------------------------------
The application monitors the following interrupt signals:

SIGNAL        ACTION               RESULT
-------------------------------------------------------------------------------
CTRL+C        Copy Command         Increment "Bites" (Feeding)
CTRL+V        Paste Command        Increment "Play" (Interaction)
CTRL+S        Save Command         Force Data Sync to Disk
CTRL+Z        Undo Command         Visual Response Only

6. EVOLUTIONARY PARAMETERS
-------------------------------------------------------------------------------
LEVEL         POINT THRESHOLD      CLASSIFICATION
-------------------------------------------------------------------------------
LV 0          0                    Hatchling
LV 1          1000                 Maru
LV 2          2000                 Scholar
LV 3          3000                 Cyber-Drake
LV 4          4000                 Void-Walker
LV 5          5000                 Star-Eater

7. DATA ARCHITECTURE
-------------------------------------------------------------------------------
* desktopotchy.py: Main executable binary
* pet_stats.json: Persistent data storage for levels and streaks

===============================================================================
                         END OF DOCUMENTATION FILE
===============================================================================
