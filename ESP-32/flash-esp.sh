# pip install esptool
python -u -m esptool --port COM4 erase_flash
python -u -m esptool --port COM4 write_flash --flash_mode keep --flash_size detect 0x1000 esp32-20230426-v1.20.0.bin