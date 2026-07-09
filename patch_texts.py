import csv
import io

path = r'D:\Clash-Of-SL\Clash SL Server\bin\Debug\Gamefiles\csv\texts_patch.csv'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    raw = f.read()

replacements = {
    '\"Welcome to the global chat.\\n\\nPlease be respectful and polite towards others. Offensive behavior is not tolerated.\\n\\nDo not share any private information (email, phone number, address, passwords)!\"': '\"ยินดีต้อนรับสู่แชตรวม\\n\\nโปรดให้เกียรติและสุภาพต่อผู้อื่น พฤติกรรมหยาบคายจะไม่ได้รับการยอมรับ\\n\\nอย่าแบ่งปันข้อมูลส่วนตัวใดๆ (อีเมล หมายเลขโทรศัพท์ ที่อยู่ รหัสผ่าน)!\"',
    '\"To report inappropriate behavior, tap on the offending message and choose \"\"Report\"\".\"': '\"หากต้องการรายงานพฤติกรรมที่ไม่เหมาะสม ให้แตะที่ข้อความและเลือก \"\"รายงาน\"\"\"'
}

for old, new in replacements.items():
    raw = raw.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(raw)
print('Texts patch updated!')
