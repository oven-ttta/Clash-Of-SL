import paramiko
import os

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

# Create images dir
ssh.exec_command("mkdir -p /root/server/images")

sftp = ssh.open_sftp()
print("Uploading Statistics.html...")
sftp.put(r"D:\Clash-Of-SL\Clash SL Server\WebAPI\HTML\Statistics.html", "/root/server/WebAPI/HTML/Statistics.html")

print("Uploading logo...")
sftp.put(r"C:\Users\MSI-Owen\.gemini\antigravity-cli\brain\9bd44f6b-ee84-4001-824a-76e30a0abbe1\owen_app_icon_1783576811593.jpg", "/root/server/images/logo.jpg")

sftp.close()

print("Files uploaded!")
