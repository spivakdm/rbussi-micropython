"""Run inside an isolated classroom container, without a physical robot."""
import ctypes as c
import os
from pathlib import Path
import re
import subprocess
import time

from PyQt5.QtWidgets import QApplication

def tree():
    return subprocess.check_output(['xwininfo', '-root', '-tree'], text=True)

def wait_for(predicate, timeout=12):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return
        app.processEvents()
        time.sleep(0.05)
    raise AssertionError('Desktop check timed out')

app = QApplication([])
x = c.CDLL('libX11.so.6')
t = c.CDLL('libXtst.so.6')
x.XOpenDisplay.restype = c.c_void_p
display = c.c_void_p(x.XOpenDisplay(b':0'))
assert display
x.XKeysymToKeycode.restype = c.c_uint

def key(symbol, down):
    code = x.XKeysymToKeycode(display, c.c_ulong(symbol))
    t.XTestFakeKeyEvent(display, code, down, 0)
    x.XSync(display, False)

def click(a, b):
    t.XTestFakeMotionEvent(display, -1, a, b, 0)
    t.XTestFakeButtonEvent(display, 1, 1, 0)
    x.XSync(display, False)
    time.sleep(0.1)
    t.XTestFakeButtonEvent(display, 1, 0, 0)
    x.XSync(display, False)
    time.sleep(0.2)

terminal = subprocess.Popen(['xterm', '-title', 'Desktop-check',
                             '-geometry', '60x12+100+100',
                             '-e', 'bash', '--noprofile', '--norc', '-i'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
graph = None
try:
    wait_for(lambda: '"Desktop-check"' in tree())
    wid = next(line.split()[0] for line in tree().splitlines() if '"Desktop-check"' in line)
    def state():
        return subprocess.check_output(['xprop', '-id', wid, '_NET_WM_STATE'], text=True)
    def button(offset):
        info = subprocess.check_output(['xwininfo', '-id', wid], text=True)
        def value(label):
            return int(re.search(label + r':\s+(-?\d+)', info)[1])
        click(value('Absolute upper-left X') + value('Width') - offset,
              value('Absolute upper-left Y') - 10)

    # Qt owns CLIPBOARD and serves it to xterm as an X11 selection.
    target = Path('/tmp/rbussi-clipboard-check')
    target.unlink(missing_ok=True)
    app.clipboard().setText("printf paste-ok > /tmp/rbussi-clipboard-check")
    app.processEvents()
    key(0xffe3, True)   # Control
    key(0xffe1, True)   # Shift
    key(ord('V'), True)
    key(ord('V'), False)
    key(0xffe1, False)
    key(0xffe3, False)
    for _ in range(20):
        app.processEvents()
        time.sleep(0.03)
    key(0xff0d, True)
    key(0xff0d, False)
    wait_for(target.exists)
    assert target.read_text() == 'paste-ok'
    print('PASS: Ctrl+Shift+V pastes CLIPBOARD', flush=True)

    button(25)
    assert 'MAXIMIZED_HORZ' in state()
    button(25)
    assert 'MAXIMIZED_HORZ' not in state()
    button(41)
    assert 'HIDDEN' in state()
    x.XMapWindow(display, c.c_ulong(int(wid, 16)))
    x.XSync(display, False)
    time.sleep(0.3)
    button(9)
    wait_for(lambda: '"Desktop-check"' not in tree())
    print('PASS: maximize, restore, minimize and close buttons', flush=True)

    count = tree().count('("xterm" "XTerm")')
    key(0xffc5, True)   # F8
    key(0xffc5, False)
    wait_for(lambda: tree().count('("xterm" "XTerm")') == count + 1)
    print('PASS: F8 opens a terminal', flush=True)

    assert 'l10n.setup([]);' in Path('/usr/share/novnc/app/ui.js').read_text()
    graph = subprocess.Popen(['ros2', 'run', 'rqt_graph', 'rqt_graph'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
    wait_for(lambda: '"rqt_graph__RosGraph - rqt"' in tree(), timeout=25)
    assert graph.poll() is None
    print('PASS: English noVNC and rqt_graph window', flush=True)
finally:
    if graph is not None and graph.poll() is None:
        import signal
        os.killpg(graph.pid, signal.SIGTERM)
    if terminal.poll() is None:
        terminal.terminate()
    x.XCloseDisplay(display)
