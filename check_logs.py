import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('103.6.168.76', username='root', password='oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z')

stdin, stdout, stderr = ssh.exec_command('tail -n 100 /root/server/Logs/log_$(ls -tr /root/server/Logs/ | tail -n 1)')
print(stdout.read().decode('utf-8', errors='replace').encode('ascii', 'ignore').decode('ascii'))
