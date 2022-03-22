# Booth Main
This consists of the QR code scanner, alcohol dispenser, and temperature sensor.

It needs the `i2c` interface to be enabled through `raspi-config`.

## Installing Dependencies

### Native
```bash
sudo apt install pip libgstreamer1.0-dev gstreamer1.0-plugins-good libzbar-dev gstreamer1.0-plugins-bad python3-gi
```

### Python
Note: Must be installed globally using `sudo -H` when running the script with cron.

```bash
pip install gspread pyyaml PyMLX90614 rpi_lcd
```

## Running
```bash
cd booth-main
python src/main.py
```

## Setting up autostart
This would automatically launch `booth-main` on Pi's startup.

Run the following command:
```bash
mkdir logs
sudo crontab -e
```

Then append the following line:

```
@reboot sh /home/pi/booth-py/booth-main/booth.sh >/home/pi/logs/cronlog 2>&1
```

## Error codes

* Camera startup error: 5s beep
* Display initialize error: 7s beep


# UV Sterilizer
This includes the UV-C sterilizer. This must be uploaded in an Arduino device.


# QR Code Generator
This generates QR Code into a folder from an Excel file with the following columns: Name, Address, Contact Number, Room ID.

## Installing Dependencies
```bash
pip install qrcode pandas openpyxl
```

## Running
```bash
python generate_qr_code/main.py -h -v excel_file_path output_file
```
