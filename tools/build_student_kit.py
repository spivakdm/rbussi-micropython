"""Build a student ZIP from an explicit list of course files."""
from pathlib import Path
import ast
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6'
NAME = 'RBussi-student-kit-v' + VERSION
FILES = [
    'robot.py',
    'docs/student-setup.md',
    'docs/quick-reference.md',
    'docs/library.md',
    'docs/firmware-and-library.md',
    'docs/wheel-calibration.md',
    'docs/wiring-reference.md',
    'Connections.png',
    'examples/00_check_setup.py',
    'examples/first_drive.py',
    'examples/01_variables.py',
    'examples/02_sequence.py',
    'examples/03_wheel_balance.py',
    'examples/04_wheel_control.py',
    'examples/05_continuous_control.py',
    'examples/stop.py',
    'worksheets/day01-observations.md',
    'firmware/ESP32_GENERIC-20260824-v1.29.0.bin',
    'firmware/MicroPython-LICENSE.txt',
    'firmware/SOURCE.md',
]
START = '''# RBussi Student Kit — v0.6

Extract this ZIP before opening its files. Start with [the setup guide](docs/student-setup.md).

In class: install Thonny during the 30-minute setup block, connect the ESP32, install or verify the supplied MicroPython firmware, and upload `robot.py` to the board.

Run `examples/00_check_setup.py` first; it requests no movement. Then use `examples/first_drive.py` with wheels lifted and the motor battery connected. Save personal programs under a new filename on your computer.

- [Firmware installation and library upload](docs/firmware-and-library.md)
- [Movement API](docs/quick-reference.md)
- [Library guide and examples](docs/library.md)
- [Wheel balance and calibration](docs/wheel-calibration.md)
- [Wiring reference and voltage check](docs/wiring-reference.md)
- [Observation worksheet](worksheets/day01-observations.md)
- [Firmware source and license information](firmware/SOURCE.md)

Baseline: Thonny 5.0.0, MicroPython 1.29.0, classic ESP32 Wemos D1 R32, class `RBussi`.

The ZIP includes firmware and course files, not Thonny installers, USB drivers, simulator software, or Moodle credentials. Get the actual course and simulator links from the instructor. Windows/macOS and student Linux installation routes still require instructor rehearsal.

`SHA256SUMS.txt` records hashes of all other kit files to detect accidental changes; it is not a signature.
'''

def main():
    payload = {name: (ROOT / name).read_bytes() for name in FILES}
    firmware = payload['firmware/ESP32_GENERIC-20260824-v1.29.0.bin']
    expected = 'e67ad6015a0a504c1fec9aa9bbf589d0432ed28e62546f4f8dd8a147f8bd95f6'
    if hashlib.sha256(firmware).hexdigest() != expected:
        raise ValueError('Firmware does not match the approved download')
    for name, data in payload.items():
        if name.endswith('.py'):
            ast.parse(data.decode('utf-8'), filename=name)
    payload['START_HERE.md'] = START.encode('utf-8')
    payload['SHA256SUMS.txt'] = ''.join(
        hashlib.sha256(data).hexdigest() + '  ' + name + '\n'
        for name, data in sorted(payload.items())
    ).encode('utf-8')
    destination = ROOT / 'dist' / (NAME + '.zip')
    destination.parent.mkdir(exist_ok=True)
    temporary = destination.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            archive.writestr(NAME + '/' + name, data)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP integrity check failed')
    temporary.replace(destination)
    print(destination)
    print(len(payload), 'files;', destination.stat().st_size, 'bytes')

if __name__ == '__main__':
    main()
