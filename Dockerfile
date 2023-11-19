FROM ubuntu:latest

# Set environment variables to avoid issues during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    wget \
    curl \
    build-essential \
    software-properties-common \
    libcairo2 \
    libcairo2-dev \
    tshark \
    libgirepository1.0-dev \
    vim

# Add the deadsnakes PPA
RUN add-apt-repository ppa:deadsnakes/ppa

# Install Python 3.12 from deadsnakes PPA
RUN apt-get update && apt-get install -y python3.12 python3.12-venv python3.12-dev

# Set Python 3.12 as the default python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Optionally, you can create a symbolic link for the pip command
# If the deadsnakes PPA does not package pip for Python 3.12, you may need to use ensurepip or get pip another way
RUN python3.12 -m ensurepip
RUN python3.12 -m pip install --upgrade pip

# Reset the environment variable
ENV DEBIAN_FRONTEND=newt

# Install rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    rm -rf $HOME/.cargo/registry

# Set environment variables
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
COPY entrypoint.sh .

# Set the entrypoint script
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

# Set the default command
CMD ["sleep", "infinity"]
