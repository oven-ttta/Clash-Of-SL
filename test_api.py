import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:88/api/")
print("With slash:", stdout.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:88/api")
print("Without slash:", stdout.read().decode('utf-8'))

ssh.close()
