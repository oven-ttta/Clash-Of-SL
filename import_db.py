import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Uploading database backup...")
sftp = ssh.open_sftp()
sftp.put(r"D:\Clash-Of-SL\cssdb_backup_utf8.sql", "/root/cssdb_backup_utf8.sql")
sftp.close()

commands = [
    "mysql cssdb < /root/cssdb_backup_utf8.sql",
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
print("Database imported successfully!")
