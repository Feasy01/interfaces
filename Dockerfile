# syntax=docker/dockerfile:1


ARG PYTHON_VERSION=3.10.12
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    python -m pip install poetry

COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
RUN apt-get update && apt-get install -y git
RUN mkdir /usr/share/desktop-directories/
RUN apt-get install -y libusb-1.0.0-dev avahi-daemon libavahi-common3 libavahi-client3 xdg-utils libqt5multimedia5-plugins libqt5scripttools5 libqt5network5 libqt5serialport5
RUN dpkg -i ./include/digilent.adept.runtime_2.27.9-amd64.deb
RUN dpkg -i ./include/digilent.waveforms_3.21.3_amd64.deb
USER appuser

# Copy the source code into the container.

# Expose the port that the application listens on.
EXPOSE 8001

# Run the application.
CMD python3 ./serve.py
