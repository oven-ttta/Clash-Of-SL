import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Uploading Statistics.html...")
sftp = ssh.open_sftp()
sftp.put(r"D:\Clash-Of-SL\Clash SL Server\WebAPI\HTML\Statistics.html", "/root/server/WebAPI/HTML/Statistics.html")
sftp.close()

ssh.close()
print("Web page uploaded successfully!")
