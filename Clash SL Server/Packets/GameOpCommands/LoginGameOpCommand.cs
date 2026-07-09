using System;
using CSS.Core;
using CSS.Core.Network;
using CSS.Logic;
using CSS.Packets.Messages.Server;

namespace CSS.Packets.GameOpCommands
{
    internal class LoginGameOpCommand : GameOpCommand
    {
        private readonly string[] m_vArgs;

        public LoginGameOpCommand(string[] args)
        {
            m_vArgs = args;
            SetRequiredAccountPrivileges(0);
        }

        public override async void Execute(Level level)
        {
            if (level.Avatar.AccountPrivileges >= GetRequiredAccountPrivileges())
            {
                if (m_vArgs.Length >= 3)
                {
                    try
                    {
                        long id = Convert.ToInt64(m_vArgs[1]);
                        string code = m_vArgs[2];

                        Level targetLevel = await ResourcesManager.GetPlayer(id);
                        if (targetLevel != null && !string.IsNullOrEmpty(targetLevel.Avatar.GoogleToken) && targetLevel.Avatar.GoogleToken.Equals(code, StringComparison.OrdinalIgnoreCase))
                        {
                            // Correct! Send the village switch packet.
                            GlobalChatLineMessage c = new GlobalChatLineMessage(level.Client)
                            {
                                Message = "เชื่อมต่อบัญชีสำเร็จ! กรุณากดยืนยันที่หน้าต่างเพื่อโหลดหมู่บ้าน",
                                HomeId = level.Avatar.UserId,
                                CurrentHomeId = level.Avatar.UserId,
                                LeagueId = 22,
                                PlayerName = "System"
                            };
                            Processor.Send(c);

                            var switchMsg = new FacebookChooseVillageMessage(level.Client, targetLevel);
                            Processor.Send(switchMsg);
                        }
                        else
                        {
                            GlobalChatLineMessage c = new GlobalChatLineMessage(level.Client)
                            {
                                Message = "บัญชี ID หรือรหัสเชื่อมต่อไม่ถูกต้อง",
                                HomeId = level.Avatar.UserId,
                                CurrentHomeId = level.Avatar.UserId,
                                LeagueId = 22,
                                PlayerName = "System"
                            };
                            Processor.Send(c);
                        }
                    }
                    catch (Exception)
                    {
                        GlobalChatLineMessage c = new GlobalChatLineMessage(level.Client)
                        {
                            Message = "รูปแบบคำสั่งไม่ถูกต้อง รูปแบบ: /login <id> <code>",
                            HomeId = level.Avatar.UserId,
                            CurrentHomeId = level.Avatar.UserId,
                            LeagueId = 22,
                            PlayerName = "System"
                        };
                        Processor.Send(c);
                    }
                }
                else
                {
                    GlobalChatLineMessage b = new GlobalChatLineMessage(level.Client)
                    {
                        Message = "รูปแบบไม่ถูกต้อง วิธีใช้: /login <id> <code>",
                        HomeId = level.Avatar.UserId,
                        CurrentHomeId = level.Avatar.UserId,
                        LeagueId = 22,
                        PlayerName = "System"
                    };
                    Processor.Send(b);
                }
            }
        }
    }
}
