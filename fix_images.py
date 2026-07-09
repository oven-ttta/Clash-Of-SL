import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

commands = [
    "mkdir -p /var/www/html/images",
    "cp /root/server/images/* /var/www/html/images/",
    "chmod -R 755 /var/www/html/images",
    "chown -R www-data:www-data /var/www/html/images"
]

for cmd in commands:
    ssh.exec_command(cmd)

# Update Nginx config
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/default")
conf = stdout.read().decode('utf-8')

if "alias /root/server/images/;" in conf:
    conf = conf.replace("alias /root/server/images/;", "alias /var/www/html/images/;")
    
    with open("temp_nginx2.conf", "w") as f:
        f.write(conf)
    
    sftp = ssh.open_sftp()
    sftp.put("temp_nginx2.conf", "/etc/nginx/sites-available/default")
    sftp.close()
    
    ssh.exec_command("systemctl restart nginx")
    print("Fixed Nginx alias and restarted!")
else:
    print("Config not found or already fixed.")

ssh.close()
