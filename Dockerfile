# Use an official CUDA base image
FROM ibeatgroup/ibeat_v2:release210


# Copy in gear metadata and wrapper
COPY manifest.json /flywheel/v0/manifest.json
COPY run.py /flywheel/v0/run.py

# Flywheel requires entrypoint through wrapper
ENTRYPOINT ["python","/flywheel/v0/run.py"]

