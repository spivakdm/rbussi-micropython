# Browser input regression check

Use an isolated container without settings.env or an MQTT bridge. Connect Chromium to its noVNC port and click the terminal. Do not run these checks on a physical robot.

1. Copy `printf paste-ok > /tmp/browser-paste-check` on the host. Press Ctrl+V in the VNC terminal without opening Clipboard. Wait for visible text, press Enter, and verify the file contains `paste-ok`.
2. Repeat with Ctrl+Shift+V and different text five times. Verify that each paste uses the new clipboard content.
3. Paste a multiline shell command with a backslash continuation and quoted text `привет café`. After Enter, verify the output is unchanged UTF-8.
4. In a disposable terminal run `IFS= read -r line; printf %s "$line" > /tmp/held-spaces`. Hold Space for 1.5 seconds, release, and press Enter. `wc -c /tmp/held-spaces` must report more than one byte. Check that repetition stops after release.
5. Verify the manual noVNC Clipboard panel still works with Shift+Insert and that normal Ctrl+C interrupts a running command.
6. On macOS, repeat the direct-paste test using Command+V (not yet verified on native macOS).

Validated in Chromium against x11vnc: five successive pastes, UTF-8 multiline paste, and 23 spaces from one 1.5-second key hold. Native browser paste supplies the text; no clipboard permission polling is used. The helper encodes the legacy x11vnc clipboard payload as UTF-8 and leaves extended-clipboard encoding to noVNC when negotiated.
