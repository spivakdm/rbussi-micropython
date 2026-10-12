# RBussi — Student Setup

Course baseline: Thonny 5.0.0, MicroPython 1.29.0, Wemos D1 R32 with ESP32 and 4 MB flash. Instructions are in English. Windows and macOS instructions still require a classroom rehearsal; the preparation robot has been tested on Linux.

## At the start of Day 1

We install Thonny together in class. The shared setup block lasts 30 minutes. Bring your laptop, charger, USB data cable, and a suitable adapter. Tell the instructor your operating system and CPU type and whether application/driver installation requires IT assistance.

1. Get the approved installer and course ZIP from the instructor.
2. Install **Thonny** using the section for your OS below, then select English for the interface.
3. Extract the ZIP into a writable folder such as `Documents/RBussi`.
4. Connect the robot, install or verify MicroPython, and upload `robot.py` using the [firmware and library guide](firmware-and-library.md).

Students install the supplied MicroPython image as a supervised activity, then upload the library. The instructor may prepare boards beforehand; those students verify the firmware or repeat installation when assigned. The shared 30-minute setup target includes these steps, with individual recovery continuing during local practice.

The standard Windows/macOS Thonny installers include desktop Python. MicroPython runs on the board. A browser provides access to Moodle and the remote lab; the instructor supplies the actual simulator and course links.

## Windows 10 or 11

- Get Thonny 5.0.0 from the [official download page](https://thonny.org/) or the instructor's approved installer.
- Choose **x64** for Intel/AMD computers; choose **ARM64** for Windows on ARM, such as a Snapdragon laptop. Check Windows Settings → System → About if unsure.
- Run the installer and launch Thonny. University-managed computers may require IT assistance.
- With the robot attached, look for a new `COM` port in Device Manager under Ports (COM & LPT). The number varies; it is not necessarily `COM3`.

Our preparation board uses a CH340 USB-to-serial converter. If no port appears, try the supplied data cable and another USB socket first. If Device Manager reports a missing driver, use the [CH340/CH341 driver from WCH](https://www.wch-ic.com/downloads/CH341SER.EXE.html?type=en) with instructor/IT help. Check driver support on Windows ARM before class. Do not install unrelated ESP32 USB drivers just because a tutorial mentions them.

## macOS

- Use the [official Thonny download](https://thonny.org/): **ARM64** for Apple Silicon (M1/M2/M3 and later), or **x64** for Intel Macs. Check Apple menu → About This Mac.
- Install the `.pkg` and open Thonny from Applications. Report installation restrictions to the instructor/IT.
- Connect the robot through a USB data cable and, where required, a data-capable USB-C adapter.
- In Thonny, look for the serial port that appears when the board is connected. Names commonly begin with `/dev/cu.`; the exact suffix varies.

Try the existing OS driver first. If the CH340 is not recognized after cable checks, follow the manufacturer's [macOS driver instructions](https://github.com/WCHSoftGroup/ch34xser_macos). Do not install a driver if the port already works.

## Linux

Use a native installation for the course. The instructor must test the instructions on your distribution; Debian/Ubuntu commands do not apply to every Linux system.

### Ubuntu, Debian, or Linux Mint

For the pinned Thonny version, use a dedicated virtual environment:

```bash
sudo apt update
sudo apt install python3-venv python3-tk
python3 -m venv "$HOME/.venvs/rbussi-thonny"
"$HOME/.venvs/rbussi-thonny/bin/python" -m pip install "thonny==5.0.0" "esptool==5.2.0"
"$HOME/.venvs/rbussi-thonny/bin/thonny"
```

This avoids installing packages into the OS-managed Python. Do not use `sudo pip`. The course instructor can provide a launcher so you do not need the last command each time.

Alternatively, the distribution's `thonny` package can be used if the instructor has checked its version and menus. For Fedora or other distributions, contact the instructor before class; [Thonny's Linux page](https://github.com/thonny/thonny/wiki/Linux) describes supported installation routes.

The board will commonly appear as `/dev/ttyUSB0`, but its number may differ. If opening the detected port reports a permission error, inspect its owner/group:

```bash
ls -l /dev/ttyUSB0
```

On Ubuntu/Debian, if the group is `dialout`, add your user:

```bash
sudo usermod -aG dialout "$USER"
```

Then **log out completely and log back in**, or reboot. Other distributions may use a different group. Do not run Thonny as root or apply world-writable permissions to the port. If a CH340 port does not appear, ask for help diagnosing the device rather than downloading a Windows driver.

## In class: connect to MicroPython

Keep motor power off during connection and firmware work. USB powers the controller for this step.

1. Connect the board and open Thonny.
2. Open **Run → Select interpreter** (or the interpreter selector at the bottom right).
3. Select **MicroPython (ESP32)** and the port belonging to your robot.
4. If the approved firmware is already installed, use the shell to verify it:

```python
import sys
print(sys.implementation)
print("Hello from RBussi")
```

Expected: the implementation is `micropython`, version 1.29.0 for the course baseline. If you see desktop Python, change the interpreter. If the board does not have MicroPython, continue with the supervised firmware step.

## In class: install firmware and upload the library

Follow the [step-by-step firmware and library guide](firmware-and-library.md). The course ZIP contains both the `.bin` firmware and `robot.py`.

Use Thonny's ESP32 installation dialog, **Select local MicroPython image ...**, and the supplied full image with address **`0x1000`**. Erase only after the instructor confirms that existing work has been preserved. After installation, verify MicroPython and upload `robot.py` again.

For a board already prepared by the instructor, verify the version and proceed to the upload unless the instructor assigns reflashing.

## Copy the library and run your first program

1. Open **View → Files** in Thonny.
2. Find the extracted kit's `robot.py` on the computer and upload it to the device root using the file browser. If using Save as instead, select the MicroPython device and keep the exact name `robot.py`.
3. Open `examples/00_check_setup.py` from the computer and run it with **F5** or **Run → Run current script**. This checks the library without moving the robot.
4. Lift the wheels and connect the motor battery.
5. Open `examples/first_drive.py` and run it. The robot should move forward briefly and stop.

```python
from robot import RBussi

with RBussi() as robot:
    robot.forward(speed=50, seconds=0.5)
```

Save your own program on the computer as `day01_first_move.py`. Keep `robot.py` for the library. Do not call your script `robot.py` or save movement code as `main.py` on the board: `main.py` runs on boot.

F5 sends the program to the board; ordinary laptop Python cannot run the MicroPython `machine` module. The library must exist on the board even when the example is stored on your computer.

## When something goes wrong

| Symptom | First action |
|---|---|
| No board port | Check the data cable, USB adapter, and whether the OS detects the board |
| Port busy | Close other serial tools and duplicate Thonny windows |
| Permission denied on Linux | Check port group membership and log in again after a group change |
| `No module named robot` | Upload `robot.py` to the board root |
| Cannot import `RBussi` | Use the current library; capitalization matters |
| `No module named machine` on the computer | Select the ESP32 MicroPython interpreter |
| Program runs but no movement | Check the separate motor battery and switch |
| Motion is unexpected | Turn off motor power; keep wheels lifted for diagnosis |

The provided timed commands stop in `finally`, and the `with` block closes the motor controller on exit. Use Stop/Restart or Ctrl+C to interrupt code, but keep the physical motor-power switch accessible: software stopping is not an independent hardware emergency stop.

## Ready checklist

At arrival: laptop and charger available, USB data connection ready, installation rights known.

In class: MicroPython responds, `00_check_setup.py` passes, first movement and stopping are physically observed, personal script saved.

References: [Thonny downloads](https://thonny.org/), [MicroPython support in Thonny](https://github.com/thonny/thonny/wiki/MicroPython), [MicroPython ESP32 firmware](https://micropython.org/download/ESP32_GENERIC/). Menu behavior was also checked against the installed Thonny 5.0.0 source. OS-specific installation has not yet been rehearsed on Windows/macOS.
