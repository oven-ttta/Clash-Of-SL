using System;
using System.Linq;
using System.Security.Cryptography;
using CSS.Core;
using CSS.Core.Network;
using CSS.Logic;
using CSS.Logic.AvatarStreamEntry;
using CSS.Packets.Messages.Server;

namespace CSS.Packets.GameOpCommands
{
    internal class LinkGameOpCommand : GameOpCommand
    {
        private readonly string[] m_vArgs;

        public LinkGameOpCommand(string[] args)
        {
            m_vArgs = args;
            SetRequiredAccountPrivileges(0);
        }

        public override void Execute(Level level)
        {
            if (level.Avatar.AccountPrivileges >= GetRequiredAccountPrivileges())
            {
                // Generate random code
                const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
                var random = new Random();
                var code = new string(
                    System.Linq.Enumerable.Repeat(chars, 8)
                        .Select(s => s[random.Next(s.Length)]).ToArray());

                level.Avatar.GoogleToken = code;
                Resources.DatabaseManager.Save(level);

                string message = $"[ระบบเชื่อมต่อบัญชี]\nรหัส Link Code ของคุณคือ: {code}\nAccount ID ของคุณคือ: {level.Avatar.UserId}\n\nในอุปกรณ์ใหม่ของคุณ ให้พิมพ์คำสั่งนี้ในช่องแชทโลก:\n/login {level.Avatar.UserId} {code}";

                GlobalChatLineMessage c = new GlobalChatLineMessage(level.Client)
                {
                    Message = message,
                    HomeId = level.Avatar.UserId,
                    CurrentHomeId = level.Avatar.UserId,
                    LeagueId = 22,
                    PlayerName = "System"
                };
                Processor.Send(c);
            }
        }
    }
}
