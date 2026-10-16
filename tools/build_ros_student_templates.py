"""Build an add-on archive for an existing ROS kit; no credentials or answers."""
from pathlib import Path
import ast
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['README.md', '01_sensor_subscriber.py', '02_velocity_publisher.py',
         '03_line_follower.py']

def main():
    destination = ROOT / 'dist/RBussi-ROS-student-templates.zip'
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            content = (ROOT / 'ros2/examples/student' / name).read_bytes()
            if name.endswith('.py'):
                ast.parse(content, filename=name)
            archive.writestr('examples/student/' + name, content)
    print(destination)

if __name__ == '__main__':
    main()
