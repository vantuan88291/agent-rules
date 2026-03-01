#!/bin/bash
# scripts/scan_devices.sh
echo "Scanning for Bluetooth devices (10 seconds)..."
timeout 10s bluetoothctl scan on > /dev/null 2>&1
echo "Recent devices found:"
bluetoothctl devices
