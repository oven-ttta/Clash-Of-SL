using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CSS.Core;
using CSS.Helpers;
using CSS.Helpers.List;
using CSS.Logic;

namespace CSS.Packets.Messages.Server
{
    internal class FacebookChooseVillageMessage : Message
    {
        public Level _Player { get; set; }

        public FacebookChooseVillageMessage(Device client, Level _Level) : base(client)
        {
            this.Identifier = 24262;
            _Player = _Level;
        }

        internal override async void Encode()
        {
            try
            {
                this.Data.AddString(null);
                this.Data.Add(1);

                this.Data.AddInt(_Player.Avatar.HighID);
                this.Data.AddInt(_Player.Avatar.LowID);

                this.Data.AddString(_Player.Avatar.UserToken);
                
                byte[] encodedAvatar = await _Player.Avatar.Encode();
                if (encodedAvatar != null)
                {
                    this.Data.AddRange(encodedAvatar);
                }
            }
            catch (Exception)
            {
            }
        }
    }
}
