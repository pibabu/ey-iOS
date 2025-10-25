FROM ubuntu:latest

# Install basic tools
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/private

# Keep container running
CMD ["sleep", "infinity"]