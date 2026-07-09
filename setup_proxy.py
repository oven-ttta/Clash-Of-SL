import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

nginx_conf = """
server {
    listen 80 default_server;
    server_name owenofsl.ovenx.shop;

    location / {
        proxy_pass http://127.0.0.1:88;
        proxy_set_header Host localhost:88;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

commands = [
    f"cat << 'EOF' > /etc/nginx/sites-available/default\n{nginx_conf}\nEOF",
    "systemctl restart nginx"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode('utf-8', errors='replace'))
    print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()
print("Proxy setup complete!")
