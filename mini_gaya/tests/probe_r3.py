import os, sys, json
pass
sys.path.insert(0, r"C:\Users\Ronak\Desktop\JARVIS\sprite")
from PySide6.QtWidgets import QApplication
app=QApplication([])
import jarvis_sprite as js, jarvis_sprite_hook as hk
S=js.RequestCard.summary
cwd=r"C:\Users\Ronak\Desktop\proj"
for p in [r"C:\Users\Ronak\Desktop\proj\..\..\..\AppData\Local\evil.ps1",
          r"C:\Users\Ronak\.claude.json", r"C:\Users\Ronak\Desktop\proj\.mcp.json",
          r"C:\Users\Ronak\Desktop\proj\.git\config", r"C:\Users\Ronak\.gitconfig",
          r"C:\Users\Ronak\Desktop\proj\.claude\settings.json"]:
    t,c,w=S("Write",{"file_path":p,"content":"x"},False,cwd if "proj" in p or "Ronak\." not in p else r"C:\Users\Ronak")
    print("complete=%s %-10s %s"%(c,w,p))
t,c,w=S("Edit",{"file_path":cwd+r"\a.py","old_string":"x","new_string":"y","replace_all":True},False,cwd)
print("Edit replace_all shown:", "replace_all" in t, c)
# hook trim drops nested tool_output key silently
flag={}
pl={"tool_name":"mcp__x__run","tool_input":{"cmd":"safe","tool_output":"rm -rf ~"}}
sh=hk.trim(pl,flag); print("trim:",sh["tool_input"],"flag:",flag)
t,c,w=S("mcp__x__run",sh["tool_input"],bool(flag),cwd); print("card:",t.replace("\n"," "),"complete=",c)
# bidi
cmd="echo ok \u202e#; ~ fr- mr\u202c"
t,c,w=S("Bash",{"command":cmd},False,cwd); print("bidi complete=",c)
class SP:
    def session_title(self,s): return ""
    def decide(self,*a,**k): pass
card=js.RequestCard(SP(),{"id":"x","payload":{"tool_name":"Bash","tool_input":{"command":cmd}},"truncated":False})
card.adjustSize(); card.grab().save("bidi.png")
