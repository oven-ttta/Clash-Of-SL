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
                    Level targetLevel = await ResourcesManager.GetPlayer(foundData.PlayerId);
                    if (targetLevel == null)
                    {
                        GlobalChatLineMessage fail = new GlobalChatLineMessage(level.Client)
                        {
                            Message = "เกิดข้อผิดพลาด: ไม่สามารถโหลดข้อมูลหมู่บ้านได้",
                            HomeId = level.Avatar.UserId,
                            CurrentHomeId = level.Avatar.UserId,
                            LeagueId = 22,
                            PlayerName = "System"
                        };
                        Processor.Send(fail);
                        return;
                    }

                    // Copy the target account's data into the current account!
                    // This avoids client crashes with FacebookChooseVillageMessage and perfectly restores their base.
                    long currentId = level.Avatar.UserId;
                    string currentToken = level.Avatar.UserToken;
                    
                    string targetAvatarJson = targetLevel.Avatar.SaveToJSON();
                    string targetGameObjectsJson = targetLevel.SaveToJSON();
                    
                    level.Avatar.LoadFromJSON(targetAvatarJson);
                    level.LoadFromJSON(targetGameObjectsJson);
                    
                    // Keep the current ID and Token so the client stays authenticated!
                    level.Avatar.UserId = currentId;
                    level.Avatar.UserToken = currentToken;
                    
                    // Disconnect from target alliance if the ID was cloned, or just let them stay in it.
                    // Saving will persist the cloned data to the current ID.
                    _ = Resources.DatabaseManager.Save(level);
                    
                    // Force the client to reload the game with the new data
                    Processor.Send(new OutOfSyncMessage(level.Client));
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
