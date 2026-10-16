// Paste browser clipboard text directly into the focused remote application.
import UI from './app/ui.js';

function inDesktop(event) {
    return UI.connected && event.target instanceof HTMLCanvasElement;
}

// Let the browser generate its native paste event instead of sending V to X11.
for (const type of ['keydown', 'keyup']) {
    window.addEventListener(type, event => {
        if (inDesktop(event) && (event.ctrlKey || event.metaKey) &&
            event.code === 'KeyV') {
            event.stopImmediatePropagation();
        }
    }, true);
}

window.addEventListener('paste', event => {
    if (!inDesktop(event) || !event.clipboardData) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const text = event.clipboardData.getData('text/plain');
    if (!text) return;
    const rfb = UI.rfb;
    // Release modifiers already forwarded before the browser paste shortcut.
    for (const [symbol, code] of [[0xffe3, 'ControlLeft'], [0xffe4, 'ControlRight'],
                                 [0xffe1, 'ShiftLeft'], [0xffe2, 'ShiftRight'],
                                 [0xffeb, 'MetaLeft'], [0xffec, 'MetaRight']]) {
        rfb.sendKey(symbol, code, false);
    }
    document.getElementById('noVNC_clipboard_text').value = text;
    // This x11vnc forwards legacy ClientCutText bytes to the UTF-8 X terminal.
    // noVNC's legacy encoder otherwise truncates non-Latin characters.
    const extended = rfb._clipboardServerCapabilitiesFormats?.[1] &&
                     rfb._clipboardServerCapabilitiesActions?.[1 << 27];
    const payload = extended ? text : Array.from(new TextEncoder().encode(text),
                                                byte => String.fromCharCode(byte)).join('');
    rfb.clipboardPasteFrom(payload);
    // Allow x11vnc to take ownership of the remote CLIPBOARD selection.
    setTimeout(() => {
        if (!UI.connected || UI.rfb !== rfb) return;
        rfb.sendKey(0xffe1, 'ShiftLeft', true);
        rfb.sendKey(0xff63, 'Insert', true);
        rfb.sendKey(0xff63, 'Insert', false);
        rfb.sendKey(0xffe1, 'ShiftLeft', false);
    }, 200);
}, true);
