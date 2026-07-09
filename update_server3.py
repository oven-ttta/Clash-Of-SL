import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

commands = [
    "cd /root/source && git pull origin main",
    "cd /root/source && mono /root/nuget.exe restore 'Clash SL Server.sln'",
    "cd /root/source && xbuild 'Clash SL Server.sln' /p:Configuration=Debug",
    "killall mono || true",
    "tmux kill-session -t css || true",
    "cp -r /root/source/'Clash SL Server'/bin/Debug/* /root/server/",
    "cp -r /root/source/'Clash SL Server'/WebAPI/HTML/* /root/server/WebAPI/HTML/ || true",
    "cd /root/server && tmux new -d -s css 'mono \"Clash SL Server.exe\"'"
]

sftp = ssh.open_sftp()
try:
    sftp.mkdir("/root/server/Database")
except:
    pass

import os
local_dir = r"D:\Clash-Of-SL\Clash SL Server\obj\Debug\edmxResourcesToEmbed\Database"
for f in ["CSSdb.csdl", "CSSdb.msl", "CSSdb.ssdl"]:
    sftp.put(os.path.join(local_dir, f), f"/root/server/Database/{f}")
    
sftp.close()

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode('utf-8', errors='replace'))
    print(stderr.read().decode('utf-8', errors='replace'))
    print(f"Exit status: {exit_status}")

ssh.close()
print("Update and deployment complete!")
