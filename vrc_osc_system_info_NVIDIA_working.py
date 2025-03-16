#!/usr/bin/env python3
import time
import psutil
import datetime
from pythonosc import udp_client
import dbus
import subprocess

# Function to get the current Linux distribution without external packages
def get_linux_distro():
    try:
        with open("/etc/os-release") as f:
            lines = f.readlines()
            # Find lines that contain "NAME" and "VERSION"
            distro_name = ""
            distro_version = ""
            for line in lines:
                if line.startswith("NAME="):
                    distro_name = line.strip().split("=")[1].replace('"', '')
                elif line.startswith("VERSION="):
                    distro_version = line.strip().split("=")[1].replace('"', '')
            return f"🐧 {distro_name} {distro_version}"
    except FileNotFoundError:
        return "🐧 Unknown Linux Distro"

# Setup OSC Client for VRChat (adjust IP and port if necessary)
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 9000)  # VRChat's default OSC port

# Function to get the current playing media info using MPRIS
def get_media_info():
    try:
        # Get the session bus
        bus = dbus.SessionBus()

        # Get all available MPRIS media players
        players = []
        for name in bus.list_names():
            if name.startswith('org.mpris.MediaPlayer2.'):
                players.append(name)

        # Try to get the media info from each player
        for player_name in players:
            try:
                player = bus.get_object(player_name, '/org/mpris/MediaPlayer2')
                metadata = player.Get('org.mpris.MediaPlayer2.Player', 'Metadata', dbus_interface='org.freedesktop.DBus.Properties')
                title = metadata.get('xesam:title', 'Unknown Title')
                artist = metadata.get('xesam:artist', ['Unknown Artist'])[0]
                 # Limit the title to 25 characters
                title = title[:25]
                artist = artist[:15]
                if title and artist:
                    return f"🎵 {title} - {artist}"  # Return title and artist without player name
            except dbus.DBusException:
                continue

        return "🎵 No media playing"

    except dbus.DBusException as e:
        print(f"DBus error: {e}")
        return "🎵 No media player detected"

# Function to get GPU usage (assuming NVIDIA GPU with nvidia-smi)
def get_gpu_usage():
    try:
        # Run nvidia-smi to get GPU stats
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free,memory.total', '--format=csv,noheader,nounits'], capture_output=True, text=True)

        # Split the result into the individual GPU stats (usage, free memory, total memory)
        gpu_stats = result.stdout.strip().split(', ')

        # Check if we have the expected number of stats (should be 3)
        if len(gpu_stats) != 3:
            return "🎮 Error retrieving GPU stats"

        # Parse GPU stats
        gpu_usage = gpu_stats[0]  # GPU usage percentage
        gpu_memory_free = round(int(gpu_stats[1]) / 1024, 1)  # Convert free memory from MB to GB
        gpu_memory_total = round(int(gpu_stats[2]) / 1024, 1)  # Convert total memory from MB to GB
        gpu_memory_used = round(gpu_memory_total - gpu_memory_free, 1)  # Calculate used memory in GB

        # Ensure the VRAM values are non-zero and correctly parsed
        if gpu_memory_free == 0 or gpu_memory_total == 0:
            return "🎮 Error retrieving GPU VRAM values"

        # Return the formatted GPU usage info
        return f"🎮 {gpu_usage}% | {gpu_memory_used}GB / {gpu_memory_total}GB"

    except Exception as e:
        print(f"Error getting GPU usage: {e}")
        return "🎮 No GPU or error retrieving GPU stats"

# Function to get CPU and RAM usage, along with CPU GHz and max RAM
def get_system_usage():
    try:
        cpu = psutil.cpu_percent(interval=1)
        cpu_ghz = round(psutil.cpu_freq().current / 1000, 2)  # CPU frequency in GHz
        ram_gb = round(psutil.virtual_memory().used / (1024**3), 1)  # Used RAM in GB
        max_ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)  # Total RAM in GB
        return cpu, cpu_ghz, ram_gb, max_ram_gb
    except Exception as e:
        print(f"Error getting system usage: {e}")
        return "Error", "Error", "Error", "Error"

# Function to get current time (only time, no date)
def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")  # Only the time

# Main loop that sends data to VRChat's OSC chat box
def send_data_to_vrchat():
    MAX_MESSAGE_LENGTH = 144  # Set max length to 144 characters

    while True:
        # Get system data
        current_time = get_current_time()  # Get the current time (only time)
        media_info = get_media_info()  # Get the current playing media info
        cpu_usage, cpu_ghz, ram_gb, max_ram_gb = get_system_usage()
        gpu_usage = get_gpu_usage()
        linux_distro = get_linux_distro()  # Get the Linux distribution

        # Prepare the message to send
        message = f"{linux_distro}\n⏰ {current_time}\n{media_info}\n💻 {cpu_usage}% @ {cpu_ghz}GHz\n💾 {ram_gb}GB / {max_ram_gb}GB\n{gpu_usage}"

        # Truncate the message if it's too long
        if len(message) > MAX_MESSAGE_LENGTH:
            print(f"Message is too long ({len(message)} characters). Truncating.")
            message = message[:MAX_MESSAGE_LENGTH]

        # Print the message to verify it will fit
        print(f"Sending message: \n{message}")

        # Send the message to VRChat's chatbox using /chatbox/input
        try:
            # Send the message immediately (b=True) to bypass the keyboard input
            osc_client.send_message("/chatbox/input", [message, True, False])
        except Exception as e:
            print(f"Error sending OSC message: {e}")

        # Wait before sending the next update (1.5 seconds)
        time.sleep(1.5)

if __name__ == "__main__":
    print("Starting VRChat OSC system info sender...")
    send_data_to_vrchat()
