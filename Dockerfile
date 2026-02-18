# Use an official CUDA base image
FROM ibeatgroup/ibeat_v2:release210

COPY ./License /InfantData/License

# Set up Flywheel gear environment
ENV FLYWHEEL="/flywheel/v0"
USER root
RUN mkdir -p $FLYWHEEL/input

# Install Python 3.9+ alongside existing Python
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for gear code
RUN python3.8 -m venv /opt/gear-env

# Install Flywheel SDK in the new environment
COPY requirements.txt /tmp/
RUN /opt/gear-env/bin/pip install --upgrade pip && \
    /opt/gear-env/bin/pip install -r /tmp/requirements.txt

# Copy in gear metadata and wrapper
COPY ./manifest.json /flywheel/v0/manifest.json
COPY ./run.py /flywheel/v0/run.py
COPY ./utils /flywheel/v0/utils
ADD ./shared /flywheel/v0/shared


RUN rm -rf /tmp/* /var/tmp/*

# --- TEMPORARY DEBUGGING STEPS ---
# Check the location of the default python3 binary
RUN which python3
# Check the location of the pip3 binary (The python associated with this is the one we want)
RUN which pip3

RUN python --version && python3 --version

RUN apt-get update && apt-get install -y zip && rm -rf /var/lib/apt/lists/*
# ---------------------------------

# Flywheel requires entrypoint through wrapper
ENTRYPOINT ["/opt/gear-env/bin/python","/flywheel/v0/run.py"]

