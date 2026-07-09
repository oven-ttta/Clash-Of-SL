import paramiko
import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('103.6.168.76', username='root', password='oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z')

stdin, stdout, stderr = ssh.exec_command('tmux capture-pane -t css -p -S -100')
print("TMUX:\n" + stdout.read().decode('utf-8', errors='replace'))
