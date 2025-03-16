#!/usr/bin/env python3
import time
import psutil
import datetime
from pythonosc import udp_client
import dbus
import subprocess

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
                if title and artist:
                    return f"🎵 {title} - {artist}"  # Return title and artist without player name
            except dbus.DBusException:
                continue

        return "🎵 No media playing"

    except dbus.DBusException as e:
        print(f"DBus error: {e}")
        return "🎵 No media player detected"

# Function to get GPU usage (works for both NVIDIA and AMD GPUs)
def get_gpu_usage():
    try:
        # First, check if it's an NVIDIA GPU
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free,memory.total', '--format=csv,noheader,nounits'], capture_output=True, text=True)
        if result.returncode == 0:  # NVIDIA GPU detected
            gpu_stats = result.stdout.strip().split(', ')
            gpu_usage = gpu_stats[0]  # GPU usage percentage
            gpu_memory_free = round(int(gpu_stats[1]) / 1024, 1)  # Convert MB to GB
            gpu_memory_total = round(int(gpu_stats[2]) / 1024, 1)  # Convert MB to GB
            return f"🎮 {gpu_usage}% | {gpu_memory_free}GB / {gpu_memory_total}GB"

        # If NVIDIA GPU is not found, check for an AMD GPU using 'sensors' (if available)
        result = subprocess.run(['sensors'], capture_output=True, text=True)
        if result.returncode == 0:  # 'sensors' command is available
            # Look for GPU usage or temperature in the output
            for line in result.stdout.splitlines():
                if 'edge' in line or 'gpu' in line:  # Check for GPU temp/usage-related lines
                    return f"🎮 AMD GPU Info: {line.strip()}"

        # If no GPU stats found (either no GPU or no relevant tool installed)
        return "🎮 No GPU or error retrieving GPU stats"

    except Exception as e:
        print(f"Error getting GPU usage: {e}")
        return "🎮 No GPU or error retrieving GPU stats"

# Function to get CPU and RAM usage
def get_system_usage():
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram_gb = round(psutil.virtual_memory().used / (1024**3), 1)  # Used RAM in GB
        return cpu, ram_gb
    except Exception as e:
        print(f"Error getting system usage: {e}")
        return "Error", "Error"

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
        cpu_usage, ram_gb = get_system_usage()
        gpu_usage = get_gpu_usage()

        # Prepare the message to send
        message = f"⏰ {current_time}\n{media_info}\n💻 {cpu_usage}%\n💾 {ram_gb}GB\n{gpu_usage}"

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
