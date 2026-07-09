import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

commands = [
    "systemctl status clash.service",
    "journalctl -u clash -n 50 --no-pager"
]

for cmd in commands:
    print(f"--- {cmd} ---")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='replace').encode('cp1252', errors='replace').decode('cp1252'))
    print(stderr.read().decode('utf-8', errors='replace').encode('cp1252', errors='replace').decode('cp1252'))

ssh.close()
