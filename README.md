#Desktopotchy: Your Keystroke Companion 👾
Desktopotchy is a minimalist, secure, and privacy-first desktop pet that lives in the corner of your screen. It evolves based on your productivity, "eating" your copy-pastes and growing alongside your projects.

#✨ Features
Privacy First: Zero keylogging. The pet only reacts to specific global hotkeys (Ctrl+C, Ctrl+V, etc.) and never records what you type.

Evolution System: 6 distinct stages of growth, from "Newborn" to "Cosmic".

Daily Streaks: Tracks how many days in a row you've spent time together.

Smart Sleep: Automatically falls asleep after 10 minutes of inactivity to stay out of your way.

#🚀 Getting Started
##1. Prerequisites
Ensure you have Python 3.x installed. You will also need the pynput library for the hotkey reactions.

Bash
pip install pynput

##2. Manual Start & Stop
To Start: Open your terminal/command prompt, navigate to the folder containing desktopotchy.py, and run:

Bash
python desktopotchy.py
To Stop: Use the built-in "Quick Quit" hotkey:

Windows/Linux: Ctrl + Q

macOS: Cmd + Q

Alternatively, you can close the terminal window where the script is running.

#🛠 Configure "Run on Startup"
For Windows 🪟
Press Win + R on your keyboard, type shell:startup, and hit Enter. This opens the Startup folder.

Right-click inside the folder and select New > Shortcut.

In the location box, type the following (replacing the paths with your actual locations):
pythonw.exe "C:\Path\To\Your\desktopotchy.py"
Note: Using pythonw.exe instead of python.exe allows the pet to run in the background without a messy terminal window popping up.

Click Next, name it "Desktopotchy", and click Finish.

#For macOS 🍎
Open the Automator app (found in Applications).

Select New Document > Application.

In the search bar, look for "Run Shell Script" and double-click it.

In the box, paste:
/usr/local/bin/python3 /Users/YOUR_NAME/Desktop/desktopotchy.py &
(Make sure to use the full path to your python3 and the script).

Save this as "Desktopotchy.app" in your Applications folder.

Go to System Settings > General > Login Items, click the + button, and add your new "Desktopotchy.app".

#🎮 How to Interact
The pet evolves as you perform your usual workflow:

Ctrl+C: Feeds the pet "Bites."

Ctrl+V: Plays with the pet.

Ctrl+S: The pet acknowledges your hard work by "Saving" its progress too.

Ctrl+Z: A little "Oops" reaction.

#📂 Files
desktopotchy.py: The main logic and UI.

pet_stats.json: Automatically created to store your level, bites, and streaks.

Pro Tip: You can click and drag the pet anywhere on your screen if it's blocking a specific button in your design software!.
