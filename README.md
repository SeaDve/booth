# Booth

### Dependencies:
```bash
sudo apt install pip python3-gi python3-gst-1.0 gstreamer1.0-plugins-good libzbar-dev gstreamer1.0-plugins-bad
```

### Python dependencies
```bash
pip install gspread pyyaml PyMLX90614
```

### Running
```bash
python src/main.py
```

# QR Code Generator

### Python dependencies
```bash
pip install qrcode pandas openpyxl
```

### Running
```bash
python generate_qr_code/main.py -h -v excel_file_path output_file
```
