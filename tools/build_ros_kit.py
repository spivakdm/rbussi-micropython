"""Build a credential-free ROS classroom archive from explicit source files."""
from pathlib import Path
import ast
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'RBussi-ROS-kit-v0.1.0'
FILES = {
    'README.md':'ros2/README.md', 'EXERCISES.md':'ros2/EXERCISES.md',
    'LESSON_PLAN.md':'ros2/LESSON_PLAN.md',
    'compose.yaml':'ros2/compose.yaml', 'Dockerfile':'ros2/Dockerfile',
    '.dockerignore':'ros2/.dockerignore', 'bridge.py':'ros2/bridge.py',
    'settings.env.example':'ros2/settings.env.example',
    'robot/main.py':'ros2/robot/main.py',
    'robot/robot.py':'robot.py',
    'robot/robot_mqtt.py':'ros2/robot/robot_mqtt.py',
    'robot/drive_command.py':'ros2/robot/drive_command.py',
    'robot/network_secrets.example.py':'ros2/robot/network_secrets.example.py',
    'robot/umqtt/__init__.py':'examples/day03/umqtt/__init__.py',
    'robot/umqtt/simple.py':'examples/day03/umqtt/simple.py',
    'robot/MicroPython-lib-LICENSE.txt':'examples/day03/MicroPython-lib-LICENSE.txt',
    'robot/SOURCES.md':'examples/day03/SOURCES.md',
    'examples/01_led.py':'ros2/examples/01_led.py',
    'examples/02_read_line.py':'ros2/examples/02_read_line.py',
    'examples/03_drive.py':'ros2/examples/03_drive.py',
}

def main():
    data = {name:(ROOT/source).read_bytes() for name,source in FILES.items()}
    for name, content in data.items():
        if name.endswith('.py'):
            ast.parse(content, filename=name)
    data['SHA256SUMS.txt'] = ''.join(hashlib.sha256(content).hexdigest()+'  '+name+'\n'
                                  for name,content in sorted(data.items())).encode()
    dest=ROOT/'dist'/(NAME+'.zip')
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in sorted(data.items()):
            z.writestr(NAME+'/'+name,content)
    print(dest, len(data),'files')

if __name__ == '__main__':main()
