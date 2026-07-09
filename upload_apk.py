import paramiko
import os
import sys

# Replace this with the path to your compiled and signed APK!
apk_path = r"C:\Users\MSI-Owen\Documents\APK Easy Tool v1.60 Portable\2-Recompiled APKs\Owen_of_sl.apk"

if not os.path.exists(apk_path):
    print(f"Error: Could not find APK at {apk_path}")
    print("Please make sure you have Compiled and Signed the APK in APK Easy Tool, and renamed it to Owen_of_sl.apk")
    input("Press Enter to exit...")
    sys.exit(1)

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

print(f"Connecting to {host}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Uploading APK to the server... (This might take a few minutes depending on your internet speed)")
sftp = ssh.open_sftp()
sftp.put(apk_path, "/root/server/WebAPI/HTML/Owen_of_sl.apk")
sftp.close()

ssh.close()
print("Upload Complete! Players can now download your game from http://103.6.168.76:88/")
input("Press Enter to exit...")
