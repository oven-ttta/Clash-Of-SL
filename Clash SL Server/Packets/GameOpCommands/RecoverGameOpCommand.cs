using System;
using System.Linq;
using System.Threading.Tasks;
using CSS.Core;
using CSS.Core.Network;
using CSS.Logic;
using CSS.Packets.Messages.Server;
using CSS.Database;
using CSS.Logic.Manager;

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
                string nameOrId = string.Join(" ", m_vArgs.Skip(1));
                long searchId = 0;
                long.TryParse(nameOrId, out searchId);
                string searchStr = "\"avatar_name\":\"" + nameOrId + "\"";

                GlobalChatLineMessage a = new GlobalChatLineMessage(level.Client)
                {
                    Message = "กำลังค้นหาบัญชี " + nameOrId + "...",
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
                        if (searchId > 0)
                        {
                            foundData = db.Player.FirstOrDefault(p => p.PlayerId == searchId);
                        }
                        
                        if (foundData == null)
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
                    
                    // Preserve the current alliance to prevent NullReferenceException in Encode()
                    long currentAllianceId = level.Avatar.AllianceId;

                    string targetAvatarJson = targetLevel.Avatar.SaveToJSON();
                    string targetGameObjectsJson = targetLevel.SaveToJSON();
                    
                    ClientAvatar newAvatar = new ClientAvatar();
                    newAvatar.LoadFromJSON(targetAvatarJson);
                    
                    newAvatar.UserId = currentId;
                    newAvatar.UserToken = currentToken;
                    newAvatar.HighID = (int)(currentId >> 32);
                    newAvatar.LowID = (int)(currentId & 0xffffffffL);
                    newAvatar.CurrentHomeId = currentId;
                    newAvatar.AllianceId = currentAllianceId;
                    
                    level.Avatar = newAvatar;
                    
                    level.GameObjectManager = new GameObjectManager(level);
                    level.WorkerManager = new WorkerManager();
                    level.LoadFromJSON(targetGameObjectsJson);
                    
                    // Disconnect from target alliance if the ID was cloned, or just let them stay in it.
                    // Saving will persist the cloned data to the current ID.
                    Resources.DatabaseManager.Save(level).Wait();
                    
                    // Force the client to reload the game with the new data
                    Processor.Send(new OutOfSyncMessage(level.Client));
                }
                else
                {
                    GlobalChatLineMessage fail = new GlobalChatLineMessage(level.Client)
                    {
                        Message = "ไม่พบบัญชีที่ระบุ: " + nameOrId,
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
                    Message = "รูปแบบไม่ถูกต้อง วิธีใช้: /recover <ชื่อ หรือ ไอดี>",
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
