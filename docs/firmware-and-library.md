# ESP32 Firmware and the RBussi Library

For Wemos D1 R32, classic ESP32, 4 MB flash. Course versions: Thonny 5.0.0 and MicroPython 1.29.0.

## Files from the instructor

Extract the course ZIP. Two files have different jobs:

| File | Purpose | Destination |
|---|---|---|
| `firmware/ESP32_GENERIC-20260824-v1.29.0.bin` | Installs the MicroPython interpreter | ESP32 flash, through the firmware installer |
| `robot.py` | Defines the `RBussi` movement class | Root of the MicroPython device filesystem |

You install firmware to make the board execute Python. You upload `robot.py` afterwards to give your programs robot commands. After a full erase, upload the library again. Editing an ordinary program does not require reflashing.

## 1. Connect the board

1. Switch **motor power off**. Connect the robot to the computer with a USB data cable.
2. Open Thonny. Use **Run → Select interpreter** and select **MicroPython (ESP32)**.
3. Select the port that appears when you connect this robot: `COM…` on Windows, `/dev/cu.…` on macOS, or usually `/dev/ttyUSB…` on Linux.
4. Close any other program using that port.

Firmware replacement can remove programs and settings already on the board. Before an erase, the instructor confirms that any existing work needing preservation has been backed up.

## 2. Install MicroPython in Thonny

These menu labels come from Thonny 5.0.0 in English. Keep the extracted firmware file on the **computer**.

1. In the ESP32 interpreter settings, click **Install or update MicroPython (esptool)**.
2. In the installation dialog, select your robot under **Target port**.
3. With **esptool 5.2.0**, choose **Family: ESP32**, **Variant: Espressif • ESP32 / WROOM**, **Version: 1.29.0**. This downloads a standard MicroPython image; our supplied binary is also an unmodified standard image.
4. To use the supplied local file with esptool 5.2.0, use the terminal fallback below. The GUI option **Select local MicroPython image ...** requires esptool 4.12.0 with Thonny 5.0.0; see the compatibility section.
5. Open the options menu and choose **Show install options**. Check **Target address = `0x1000`** for this full classic-ESP32 image.
6. For a clean installation on the course board, enable **Erase all flash before installing**, after the instructor's backup check. Use **115200** if you need a conservative transfer rate.
7. Click **Install**. Leave USB connected and wait for successful completion. This takes a few minutes depending on the transfer rate and computer.
8. Close the dialog, reconnect to the selected interpreter, and use Thonny's **Stop/Restart backend** button if needed. A board reset may be needed after flashing.

If Thonny reports that `esptool` is missing, open **Tools → Manage plug-ins**, install `esptool` version **5.2.0**, then restart Thonny. This is particularly relevant to Linux/pip installations. The course Linux command installs it in the same environment as Thonny.

If connection fails, check the cable, serial-port access, and competing applications first. With instructor help, boards that have BOOT and RESET/EN buttons can be placed in download mode by holding BOOT, briefly pressing/releasing RESET/EN, then releasing BOOT when the installer connects. Do not assume every D1 R32 clone has the same buttons.

## 3. Verify the interpreter

In the Thonny shell:

```python
import sys
print(sys.implementation)
print("Hello from ESP32")
```

Expected: `micropython`, version `1.29.0`, an ESP32 build, and your printed message. A desktop Python result means that the wrong interpreter is selected.

**If the instructor already flashed your board:** run this check and proceed to the library upload. Reinstall only if the instructor assigns the flashing exercise or the version needs replacement. Reflashing a prepared board erases its files when the erase option is enabled.

## 4. Upload `robot.py`

1. Open **View → Files** in Thonny.
2. In the computer file pane, find the extracted kit's `robot.py`.
3. Open the device root in the MicroPython pane. Upload the computer file there using its context menu, or open it and use **File → Save as → MicroPython device**, keeping the exact name `robot.py`.
4. Check that `robot.py` appears in the **device** pane, at the root rather than inside another folder.
5. Open `examples/00_check_setup.py` from the computer and press **F5**.

Expected output includes:

```text
RBussi ready. No movement requested.
```

If you previously imported an older library version, restart the backend after uploading so Python imports the new copy. Save your own script under a different name, for example `day01_first_move.py`.

## 5. First movement

Lift the wheels and connect motor power. Open `examples/first_drive.py` and press **F5**:

```python
from robot import RBussi

with RBussi() as robot:
    robot.forward(speed=50, seconds=0.5)
```

Confirm that both wheels turn forward and stop. Keep the motor-power switch accessible. Save this student program on the computer. For Day 1, keep movement out of `main.py`, which executes on board startup.

## Ready checkpoint

- [ ] My firmware check identifies MicroPython on ESP32.
- [ ] `robot.py` exists at the device root.
- [ ] `00_check_setup.py` imports `RBussi` without movement.
- [ ] I observed the first short movement and its stop.

## Thonny 5.0.0 and esptool compatibility

The course now uses **esptool 5.2.0** with standard image selection or direct terminal flashing. Use **esptool 4.12.0** only if you need Thonny 5.0.0's local-image picker. Thonny 5.0.0 calls `image_info --version 2` to recognize a selected file. esptool 5.2 rejects that option, so the file selection does not complete and Install may remain disabled. This is a host-tool compatibility issue, not a firmware problem. The supplied `.bin` needs no modification.

The official Linux installer checked on 12 October 2026 installed esptool 5.2.0. Only if you need the local GUI picker, use **Tools → Manage plug-ins**, find `esptool`, select version **4.12.0** in the version/advanced installation options, install it, and restart Thonny. For an installation made with the official Linux script, the terminal equivalent is:

```bash
"$HOME/apps/thonny/bin/python" -m pip install "esptool==4.12.0"
```

Recognition of the supplied image was reproduced with the exact Thonny command: esptool 5.2.0 rejected it; 4.12.0 identified ESP32 correctly. Actual GUI flashing on each student OS still needs rehearsal.

The supplied image is an unmodified standard MicroPython image, not a custom robot firmware. As an alternative to selecting a local file, select **ESP32 → Espressif • ESP32 / WROOM → 1.29.0** in Thonny's online image list. Upload `robot.py` afterwards; erasing flash removes existing files.

## Terminal fallback: flash the supplied binary with esptool 5.2.0

Close Thonny to release the USB port and switch motor power off. Open a terminal in the extracted kit folder. This command uses the Python environment created by the official Linux Thonny installer:

```bash
"$HOME/apps/thonny/bin/python" -m esptool \
  --chip esp32 --port /dev/ttyUSB0 --baud 115200 \
  write-flash --erase-all 0x1000 \
  firmware/ESP32_GENERIC-20260824-v1.29.0.bin
```

For the manual Linux installation in the setup guide, replace the Python path with `"$HOME/.venvs/rbussi-thonny/bin/python"`. Replace `/dev/ttyUSB0` with the actual port. The backslash line continuations above are Linux/macOS shell syntax.

For other environments, use the Python executable where esptool 5.2.0 is installed. For example, this is the same command on one line (also suitable for PowerShell after replacing `python` and `COM5` with your actual interpreter and port):

```text
python -m esptool --chip esp32 --port COM5 --baud 115200 write-flash --erase-all 0x1000 firmware/ESP32_GENERIC-20260824-v1.29.0.bin
```

`--erase-all` deletes all board files. Preserve needed work first. After completion, reopen Thonny, connect to MicroPython (ESP32), and upload `robot.py` again.

Read-only checks with the same environment:

```bash
"$HOME/apps/thonny/bin/python" -m esptool version
"$HOME/apps/thonny/bin/python" -m esptool image-info firmware/ESP32_GENERIC-20260824-v1.29.0.bin
```

esptool 5.2.0 command help and local image recognition were checked on the instructor's machine. This fallback command was not used to erase or flash the robot during preparation of this slide.

## Sources and verification basis

The full firmware image and its `0x1000` installation address follow the [official ESP32_GENERIC instructions](https://micropython.org/download/ESP32_GENERIC/). The file-transfer and interpreter workflow follows [Thonny's MicroPython documentation](https://github.com/thonny/thonny/wiki/MicroPython). Local-image menu labels and the missing-esptool recovery path were checked against the installed Thonny 5.0.0 source. GUI flashing still requires rehearsal on the student operating systems; the preparation robot was flashed with esptool on Linux.
