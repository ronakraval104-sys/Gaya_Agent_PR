import sys
sys.path.insert(0, r"C:\Users\Ronak\Desktop\JARVIS\sprite")
from PySide6.QtWidgets import QApplication
app=QApplication([])
import gaya_sprite as js
class SP:
    def session_title(self,s): return ""
    def decide(self,*a,**k): pass
    def place_bubble(self,*a): pass
def card(tool, ti, cwd=r"C:\Users\Ronak"):
    c=js.RequestCard(SP(),{"id":"x","payload":{"tool_name":tool,"tool_input":ti,"cwd":cwd},"truncated":False})
    allow=[b for b in c.decide_buttons if b.text()=="Allow"][0]
    return allow.isEnabled()
print("plain bash        allow:", card("Bash",{"command":"echo hi"}))
print("bidi bash         allow:", card("Bash",{"command":"echo ok \u202e#; ~ fr- mr\u202c"}))
print("bidi in MCP arg   allow:", card("mcp__x__run",{"cmd":"a\u202eb"}))
print("var-selector      allow:", card("Bash",{"command":"echo x\ufe0f\U000e0100"}))
print("hangul filler     allow:", card("Bash",{"command":"node -e \"\u3164=1\""}))
print("8.3 .claude agent allow:", card("Write",{"file_path":r"C:\Users\Ronak\CLAUDE~1\agents\edidth.md","content":"x"}))
print("8.3 .jarvis tool  allow:", card("Write",{"file_path":r"C:\Users\Ronak\JARVIS~1\tools\quote_lint.py","content":"x"}))
print("long .claude      allow:", card("Write",{"file_path":r"C:\Users\Ronak\.claude\agents\edidth.md","content":"x"}))
