import os

path = r"C:\Users\MSI-Owen\Documents\APK Easy Tool v1.60 Portable\1-Decompiled APKs\Clash of SL 8.709.1v\lib\armeabi-v7a\libg.so"

with open(path, "rb") as f:
    data = f.read()

old_ip = b"192.168.1.237"
# The new IP is 103.6.168.76 (12 chars). We pad it with \x00 to match 13 chars of the old IP.
new_ip = b"103.6.168.76\x00"

if old_ip in data:
    print(f"Found {old_ip} in libg.so. Patching...")
    new_data = data.replace(old_ip, new_ip)
    
    with open(path, "wb") as f:
        f.write(new_data)
    print("Patched successfully!")
else:
    print(f"{old_ip} not found in libg.so!")
