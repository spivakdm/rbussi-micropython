FROM ros:jazzy-ros-base
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv ros-jazzy-rmw-cyclonedds-cpp ros-jazzy-turtlesim \
    xvfb x11-utils x11vnc openbox xterm novnc websockify supervisor \
    fonts-dejavu-core librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv --system-site-packages /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir paho-mqtt==2.1.0
ENV PATH="/opt/venv/bin:$PATH" \
    RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
    PYTHONUNBUFFERED=1 DISPLAY=:0 QT_X11_NO_MITSHM=1
WORKDIR /course
COPY bridge.py /course/bridge.py
COPY examples /course/examples
COPY assets /course/assets
COPY desktop /course/desktop
RUN chmod +x /course/desktop/*.sh /course/desktop/robot-connect /course/desktop/ros-terminal \
    && ln -s /course/desktop/robot-connect /usr/local/bin/robot-connect \
    && ln -s /course/desktop/ros-terminal /usr/local/bin/ros-terminal \
    && mkdir -p /root/.config/openbox \
    && cp /course/desktop/rc.xml /root/.config/openbox/rc.xml \
    && echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc \
    && rsvg-convert -w 45 -h 45 /course/assets/rbussi-top.svg -o /course/assets/rbussi-top.png \
    && for image in /opt/ros/jazzy/share/turtlesim/images/*.png; do cp /course/assets/rbussi-top.png "$image"; done
EXPOSE 6080
CMD ["/usr/bin/supervisord", "-c", "/course/desktop/supervisord.conf"]
