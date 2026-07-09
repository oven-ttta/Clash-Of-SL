import paramiko
import re

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/default")
conf = stdout.read().decode('utf-8')

if "location /images/" not in conf:
    conf = conf.replace("location / {", "location /images/ {\n        alias /root/server/images/;\n    }\n\n    location / {")
    
    # Save back
    # Write to a temp file then upload via SFTP
    with open("temp_nginx.conf", "w") as f:
        f.write(conf)
    
    sftp = ssh.open_sftp()
    sftp.put("temp_nginx.conf", "/etc/nginx/sites-available/default")
    sftp.close()
    
    ssh.exec_command("systemctl restart nginx")
    print("Updated Nginx config and restarted!")
else:
    print("Already updated!")

ssh.close()
