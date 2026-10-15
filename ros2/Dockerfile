FROM ros:jazzy-ros-base
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv ros-jazzy-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv --system-site-packages /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir paho-mqtt==2.1.0
ENV PATH="/opt/venv/bin:$PATH" \
    RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
    PYTHONUNBUFFERED=1
WORKDIR /course
COPY bridge.py /course/bridge.py
COPY examples /course/examples
RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc
CMD ["python", "/course/bridge.py"]
