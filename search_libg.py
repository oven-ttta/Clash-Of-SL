import re

path = r"C:\Users\MSI-Owen\Documents\APK Easy Tool v1.60 Portable\1-Decompiled APKs\Clash of SL 8.709.1v\lib\armeabi-v7a\libg.so"

with open(path, "rb") as f:
    data = f.read()

# Extract all printable ASCII strings of length > 6
strings = re.findall(b"[ -~]{6,}", data)

# Search for typical IP patterns or hostnames
for s in strings:
    s_str = s.decode('ascii', errors='ignore')
    if re.search(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', s_str):
        print(f"Found IP: {s_str}")
    elif "clashofclans" in s_str:
        print(f"Found Host: {s_str}")
    elif "localhost" in s_str:
        print(f"Found localhost: {s_str}")
