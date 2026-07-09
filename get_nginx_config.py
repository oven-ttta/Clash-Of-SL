import paramiko
host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)
stdin, stdout, stderr = ssh.exec_command("curl -k -s -i https://localhost/images/logo.jpg -H 'Host: owenofsl.ovenx.shop'")
print(stdout.read().decode('utf-8'))
ssh.close()
