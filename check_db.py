import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('103.6.168.76', username='root', password='oW4i%8S;$/5Tnsz0EL(7uKa75ujz(QnkpkV%9`x4JA]0Tm1~^z')

cs_code = """
using System;
using System.IO;
using System.Reflection;
using CSS.Core;
using CSS.Logic;
using CSS.Packets.Messages.Server;

public class Test
{
    public static void Main()
    {
        try 
        {
            Console.WriteLine("Starting test...");
            // We can't easily initialize the full server, but we can try to instantiate a level from a known JSON.
            // Let's just create a dummy Level and see if FacebookChooseVillageMessage throws!
            Level l = new Level();
            l.Avatar.Initialize();
            l.Avatar.UserId = 12345;
            l.Avatar.UserToken = "dummy_token";
            
            Console.WriteLine("Encoding FacebookChooseVillageMessage...");
            var msg = new FacebookChooseVillageMessage(null, l);
            msg.Encode();
            Console.WriteLine("Data length: " + msg.Data.Count);
            Console.WriteLine("Success!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex);
        }
    }
}
"""

stdin, stdout, stderr = ssh.exec_command(f'cat << \'EOF\' > /root/test.cs\n{cs_code}\nEOF\nmcs -reference:"/root/server/Clash SL Server.exe" /root/test.cs && mono /root/test.exe')
print("STDOUT:", stdout.read().decode('utf-8', errors='replace'))
print("STDERR:", stderr.read().decode('utf-8', errors='replace'))
