import paramiko

host = "103.6.168.76"
user = "root"
password = "oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

# Note: The database name in Clash SL is usually `css` or `clash_of_clans` or `clash_sl`.
# Let's check which databases exist and add to `clash` or `css`.
stdin, stdout, stderr = ssh.exec_command("mysql -e 'SHOW DATABASES;'")
print(stdout.read().decode())

sql = """
CREATE TABLE IF NOT EXISTS cssdb.users (
  id int(11) NOT NULL AUTO_INCREMENT,
  username varchar(50) NOT NULL,
  password_hash varchar(255) NOT NULL,
  player_id bigint(20) DEFAULT NULL,
  user_token varchar(255) DEFAULT NULL,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""
stdin, stdout, stderr = ssh.exec_command(f'mysql -e "{sql}"')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
