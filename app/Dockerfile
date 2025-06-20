# Use Raspberry Pi-compatible Python image
FROM python:3.11-slim

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    git \
    cmake \
    make \
    g++ \
    libboost-python-dev \
    libboost-system-dev \
    libboost-thread-dev \
    hostapd \
    dnsmasq \
    iproute2 \
    iptables \
    iw \
    net-tools && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
# RUN pip3 install Flask RPi.GPIO
#RUN pip install --no-cache-dir -r requirements.txt

# Clone and build RF24 from source
# RUN git clone https://github.com/nRF24/RF24.git /tmp/RF24 && \
#     cd /tmp/RF24 && \
#     mkdir build && cd build && \
#     cmake .. && \
#     make && \
#     make install && \
#     cd ../pyRF24 && \
#     python3 setup.py install && \
#     rm -rf /tmp/RF24

ARG VERSION
ENV B_NUM=$VERSION

WORKDIR ~/

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# CMD gunicorn --bind 0.0.0.0:5000 wsgi:app

# Run the Flask app
# CMD ["python3", "app.py"]
CMD ["sh", "-c", "dnsmasq --conf-file=dnsmasq.conf && python app.py"]
