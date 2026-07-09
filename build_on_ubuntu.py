import paramiko
import os
import zipfile

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

# Zip the source
print("Zipping source...")
zip_path = r"D:\Clash-Of-SL\source.zip"
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(r"D:\Clash-Of-SL\Clash SL Server"):
        for file in files:
            if "bin" not in root and "obj" not in root:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, r"D:\Clash-Of-SL")
                zipf.write(file_path, arcname)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Uploading source.zip...")
sftp = ssh.open_sftp()
sftp.put(zip_path, "/root/source.zip")
sftp.close()

commands = [
    "apt-get install -y unzip mono-devel mono-xbuild",
    "rm -rf /root/source",
    "mkdir -p /root/source",
    "unzip -o /root/source.zip -d /root/source",
    "cd '/root/source/Clash SL Server' && xbuild 'Clash SL Server.csproj' /p:Configuration=Release",
    "cp '/root/source/Clash SL Server/bin/Release/Clash SL Server.exe' '/root/server/Clash SL Server.exe'",
    "systemctl restart clash.service"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode('utf-8', errors='replace').encode('cp1252', errors='replace').decode('cp1252'))
    print(stderr.read().decode('utf-8', errors='replace').encode('cp1252', errors='replace').decode('cp1252'))
    print(f"Exit status: {exit_status}")

ssh.close()
print("Built and deployed successfully!")
