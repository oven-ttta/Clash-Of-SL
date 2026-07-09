using System.Collections.Generic;
using CSS.Helpers.List;
using CSS.Logic;

namespace CSS.Packets.Messages.Server
{
    // Packets 24411
    internal class AvatarStreamMessage : Message
    {
        public AvatarStreamMessage(Device client,int _type) : base(client)
        {
            this.Identifier = 24411;
            this.Type = _type;
        }

        public int Type;

        internal override void Encode()
        {
            this.Data.AddInt(0); //Stream Ammount
        }
    }
}
