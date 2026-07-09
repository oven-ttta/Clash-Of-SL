import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

service_file = """[Unit]
Description=Clash SL Server
After=network.target mariadb.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/server
ExecStart=/usr/bin/mono "Clash SL Server.exe"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

commands = [
    # Kill the tmux session to prevent conflicts
    "tmux kill-session -t css || true",
    "killall mono || true",
    # Create systemd service file
    f"echo '{service_file}' > /etc/systemd/system/clash.service",
    # Reload daemon
    "systemctl daemon-reload",
    # Enable on boot
    "systemctl enable clash.service",
    # Start the service
    "systemctl restart clash.service"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode('utf-8', errors='replace').encode('cp1252', errors='replace').decode('cp1252'))
    print(stderr.read().decode('utf-8', errors='replace').encode('cp1252', errors='replace').decode('cp1252'))
    print(f"Exit status: {exit_status}")

# Verify it's running
print("Checking status...")
stdin, stdout, stderr = ssh.exec_command("systemctl status clash.service")
print(stdout.read().decode('utf-8', errors='replace').encode('cp1252', errors='replace').decode('cp1252'))

ssh.close()
print("Autostart setup complete!")
