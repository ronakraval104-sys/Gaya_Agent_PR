import os, sys, time
os.environ["QT_QPA_PLATFORM"]="offscreen"
sys.path.insert(0, r"C:\Users\Ronak\Desktop\JARVIS\sprite")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
app=QApplication([])
import jarvis_sprite as js
class S:
    def session_title(self, s): return ""
    def decide(self,*a,**k): pass
req={"id":"x","payload":{"tool_name":"Bash","tool_input":{"command":"ls"}},"truncated":False}
c=js.RequestCard(S(), req)
c.arm()                                  # card appears t=0
QTimer.singleShot(600, c.arm)            # card moves at t=600 (card above it closed)
QTimer.singleShot(720, lambda: print("t=720ms (120ms after move) Allow enabled:", c.decide_buttons[0].isEnabled()))
QTimer.singleShot(900, app.quit)
app.exec()
