import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

# Upload nuget.exe
sftp = ssh.open_sftp()
sftp.put(r"D:\Clash-Of-SL\nuget.exe", "/root/nuget.exe")
sftp.close()

commands = [
    "apt-get update && apt-get install -y mono-complete",
    "cd /root/source/'Clash SL Server' && mono /root/nuget.exe restore 'Clash SL Server.sln'",
    "cd /root/source/'Clash SL Server' && msbuild 'Clash SL Server.csproj' /p:Configuration=Debug",
    "killall mono || true",
    "tmux kill-session -t css || true",
    "cp -r /root/source/'Clash SL Server'/bin/Debug/* /root/server/",
    "cd /root/server && tmux new -d -s css 'mono \"Clash SL Server.exe\"'"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode('utf-8', errors='replace'))
    print(stderr.read().decode('utf-8', errors='replace'))
    print(f"Exit status: {exit_status}")

ssh.close()
print("Update and deployment complete!")
