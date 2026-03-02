---
name: pi-manager
description: Comprehensive Raspberry Pi management. Handles power (shutdown/reboot), automation (cronjobs), Bluetooth connectivity, and system monitoring (CPU/RAM/Storage). Use for any Pi hardware or OS-level management tasks.
---

# PI Manager (Consolidated)

The primary tool for managing Tuấn's Raspberry Pi 5.

## 1. Power Actions
- **Shutdown Now**: `sudo shutdown -h now`
- **Reboot Now**: `sudo reboot`
- **Scheduled Shutdown**: `sudo shutdown -h +[minutes]`
- **Cancel Shutdown**: `sudo shutdown -c`

## 2. Automation (Cronjobs)
- **List Jobs**: `crontab -l`
- **Add Daily Shutdown (11 PM)**: `(crontab -l ; echo "0 23 * * * /sbin/shutdown -h now") | crontab -`
- **Clear All Cronjobs**: `crontab -r`

## 3. Bluetooth Management
- **Status**: `bluetoothctl show`
- **Connected Devices**: `bluetoothctl devices Connected`
- **Paired Devices**: `bluetoothctl devices`
- **Scan (10s)**: Run `scripts/scan_devices.sh`
- **Connect/Disconnect**: `bluetoothctl connect [MAC]` / `bluetoothctl disconnect [MAC]`
- **Pair/Trust/Remove**: `bluetoothctl pair [MAC]`, `bluetoothctl trust [MAC]`, `bluetoothctl remove [MAC]`
- **Power ON/OFF**: `bluetoothctl power on` / `bluetoothctl power off`

## 4. System Monitoring & Storage
- **Quick Status**: `vcgencmd measure_temp && free -h && uptime`
- **Storage Usage**: `df -h /`
- **Check External Drives**: `lsblk`
- **CPU Clock**: `vcgencmd measure_clock arm`

## 5. Network Status
- **Local IP**: `hostname -I`
- **Public IP**: `curl -s https://ifconfig.me`
- **Tailscale Status**: `tailscale status`

## 6. Audio Management
- **Check Volume**: `wpctl get-volume @DEFAULT_AUDIO_SINK@`
- **Increase Volume (5%)**: `wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+`
- **Decrease Volume (5%)**: `wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-`
- **Mute/Unmute**: `wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle`

## 7. Process Management
- **Kill Chromium/Chrome**: `pkill chromium` or `pkill chrome`
- **List Top Processes**: `top -b -n 1 | head -n 20`


