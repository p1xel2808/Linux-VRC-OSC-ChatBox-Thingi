On Arch Linux

    Update your system (optional but recommended):

sudo pacman -Syu

Install required packages:

    python, python-pip, python-psutil, python-tk, python-dbus, python-osc

sudo pacman -S python python-pip python-psutil python-tk dbus-python

Install NVIDIA drivers and utilities (only needed if you want GPU stats):

    sudo pacman -S nvidia nvidia-utils

On Ubuntu

    Update your system (optional but recommended):

sudo apt update && sudo apt upgrade

Install required packages:

    python3, python3-pip, python3-psutil, python3-tk, python3-dbus, python3-osc

sudo apt install python3 python3-pip python3-psutil python3-tk python3-dbus

Install NVIDIA drivers and utilities (only needed if you want GPU stats):

    sudo apt install nvidia-driver nvidia-utils

Step 2: Install Python Dependencies via pip

Once you have the system dependencies installed, you need to install the Python libraries used by the script.

    Install the required Python libraries:

    pip3 install python-osc psutil dbus-python

Step 3: Running the Script

    Make the script executable: If you have saved your script in a file, for example system_info_vrchat.py, make sure it's executable:

chmod +x system_info_vrchat.py

Run the script: You can run the script using Python:

    python3 system_info_vrchat.py

    This will start the GUI and the script will begin monitoring system stats and sending them to VRChat (via OSC). The GUI allows you to toggle the information you want to send (CPU, RAM, GPU, media info, time, etc.).

