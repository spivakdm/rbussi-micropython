"""Build a credential-free ROS classroom archive from explicit source files."""
from pathlib import Path
import ast
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'RBussi-ROS-kit-v0.2.7'
FILES = {
    'README.md':'ros2/README.md', 'EXERCISES.md':'ros2/EXERCISES.md',
    'LESSON_PLAN.md':'ros2/LESSON_PLAN.md',
    'compose.yaml':'ros2/compose.yaml', 'Dockerfile':'ros2/Dockerfile',
    '.dockerignore':'ros2/.dockerignore', 'bridge.py':'ros2/bridge.py',
    'settings.env.example':'ros2/settings.env.example',
    'SIMULATOR.md':'ros2/SIMULATOR.md',
    'LINE_FOLLOWING.md':'ros2/LINE_FOLLOWING.md',
    'assets/rbussi-top.svg':'ros2/assets/rbussi-top.svg',
    'assets/README.md':'ros2/assets/README.md',
    'desktop/wait-display.sh':'ros2/desktop/wait-display.sh',
    'desktop/start-terminal.sh':'ros2/desktop/start-terminal.sh',
    'desktop/start-sim.sh':'ros2/desktop/start-sim.sh',
    'desktop/robot-connect':'ros2/desktop/robot-connect',
    'desktop/ros-terminal':'ros2/desktop/ros-terminal',
    'desktop/supervisord.conf':'ros2/desktop/supervisord.conf',
    'desktop/rc.xml':'ros2/desktop/rc.xml',
    'desktop/menu.xml':'ros2/desktop/menu.xml',
    'desktop/Xdefaults':'ros2/desktop/Xdefaults',
    'desktop/browser-paste.js':'ros2/desktop/browser-paste.js',
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

for source in sorted((ROOT / 'ros2/turtlesim-map').rglob('*')):
    if source.is_file():
        FILES[str(source.relative_to(ROOT / 'ros2'))] = str(source.relative_to(ROOT))
FILES['assets/riihimaki-map.png'] = 'ros2/assets/riihimaki-map.png'
FILES['assets/RIIHIMAKI-MAP-NOTICE.txt'] = 'ros2/assets/RIIHIMAKI-MAP-NOTICE.txt'

FILES['simulation/line_world.py'] = 'ros2/simulation/line_world.py'

FILES['simulation/line_geometry.py'] = 'ros2/simulation/line_geometry.py'

FILES['examples/04_sim_line_reader.py'] = 'ros2/examples/04_sim_line_reader.py'

FILES['examples/05_sim_line_follower.py'] = 'ros2/examples/05_sim_line_follower.py'

FILES['desktop/sim-line-track'] = 'ros2/desktop/sim-line-track'

FILES['desktop/sim-line-demo'] = 'ros2/desktop/sim-line-demo'

for name in ('README.md', '01_sensor_subscriber.py', '02_velocity_publisher.py',
             '03_line_follower.py'):
    FILES['examples/student/' + name] = 'ros2/examples/student/' + name

def main():
    data = {name:(ROOT/source).read_bytes() for name,source in FILES.items()}
    for name, content in data.items():
        if name.endswith('.py'):
            ast.parse(content, filename=name)
    template = ast.parse(data['robot/network_secrets.example.py'])
    values = {node.targets[0].id: ast.literal_eval(node.value)
              for node in template.body if isinstance(node, ast.Assign)}
    for key, expected in {'WIFI_SSID':'YOUR_2_4_GHZ_WIFI',
                          'WIFI_PASSWORD':'YOUR_WIFI_PASSWORD',
                          'MQTT_USER':'YOUR_ASSIGNED_USERNAME',
                          'MQTT_PASSWORD':'YOUR_ASSIGNED_PASSWORD'}.items():
        if values.get(key) != expected:
            raise ValueError('Use placeholder credentials in the public template: ' + key)
    data['SHA256SUMS.txt'] = ''.join(hashlib.sha256(content).hexdigest()+'  '+name+'\n'
                                  for name,content in sorted(data.items())).encode()
    dest=ROOT/'dist'/(NAME+'.zip')
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in sorted(data.items()):
            z.writestr(NAME+'/'+name,content)
    print(dest, len(data),'files')

if __name__ == '__main__':main()
