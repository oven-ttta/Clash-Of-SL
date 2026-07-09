import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

commands = [
    "apt-get update && apt-get install -y certbot python3-certbot-nginx",
    "certbot --nginx -d owenofsl.ovenx.shop --non-interactive --agree-tos -m admin@ovenx.shop --redirect",
    "ufw allow 443/tcp",
    "ufw reload"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode('utf-8', errors='replace'))
    print(stderr.read().decode('utf-8', errors='replace'))
    print(f"Exit status: {exit_status}")

ssh.close()
print("SSL setup complete!")
