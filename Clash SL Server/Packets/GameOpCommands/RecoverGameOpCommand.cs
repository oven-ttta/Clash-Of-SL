using System;
using System.Linq;
using System.Threading.Tasks;
using CSS.Core;
using CSS.Core.Network;
using CSS.Logic;
using CSS.Packets.Messages.Server;
using CSS.Database;

namespace CSS.Packets.GameOpCommands
{
    internal class RecoverGameOpCommand : GameOpCommand
    {
        private readonly string[] m_vArgs;

        public RecoverGameOpCommand(string[] args)
        {
            m_vArgs = args;
            SetRequiredAccountPrivileges(0);
        }

        public override async void Execute(Level level)
        {
            if (m_vArgs.Length >= 2)
            {
                string name = string.Join(" ", m_vArgs.Skip(1));
                string searchStr = "\"avatar_name\":\"" + name + "\"";

                GlobalChatLineMessage a = new GlobalChatLineMessage(level.Client)
                {
                    Message = "กำลังค้นหาบัญชีที่ชื่อ " + name + "...",
                    HomeId = level.Avatar.UserId,
                    CurrentHomeId = level.Avatar.UserId,
                    LeagueId = 22,
                    PlayerName = "System"
                };
                Processor.Send(a);

                Player foundData = null;
                await Task.Run(() =>
                {
                    using (Mysql db = new Mysql())
                    {
                        var list = db.Player.ToList();
                        foreach (var p in list)
                        {
                            if (p.Avatar.IndexOf(searchStr, StringComparison.OrdinalIgnoreCase) >= 0)
                            {
                                foundData = p;
                                break;
                            }
                        }
                    }
                });

                if (foundData != null)
                {
                    Level targetLevel = new Level();
                    targetLevel.Avatar.LoadFromJSON(foundData.Avatar);
                    targetLevel.LoadFromJSON(foundData.GameObjects);

                    GlobalChatLineMessage success = new GlobalChatLineMessage(level.Client)
                    {
                        Message = "พบบัญชี ID: " + targetLevel.Avatar.UserId + " กรุณากดยืนยันเพื่อสลับบัญชี",
                        HomeId = level.Avatar.UserId,
                        CurrentHomeId = level.Avatar.UserId,
                        LeagueId = 22,
                        PlayerName = "System"
                    };
                    Processor.Send(success);

                    var switchMsg = new FacebookChooseVillageMessage(level.Client, targetLevel);
                    Processor.Send(switchMsg);
                }
                else
                {
                    GlobalChatLineMessage fail = new GlobalChatLineMessage(level.Client)
                    {
                        Message = "ไม่พบบัญชีที่ใช้ชื่อ: " + name,
                        HomeId = level.Avatar.UserId,
                        CurrentHomeId = level.Avatar.UserId,
                        LeagueId = 22,
                        PlayerName = "System"
                    };
                    Processor.Send(fail);
                }
            }
            else
            {
                GlobalChatLineMessage b = new GlobalChatLineMessage(level.Client)
                {
                    Message = "รูปแบบไม่ถูกต้อง วิธีใช้: /recover <ชื่อในเกม>",
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
