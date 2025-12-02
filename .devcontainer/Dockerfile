# Dev Container: Data Science Ubuntu 24.04
# Author: Angel Martinez-Tenor (updated by Grok)
# Date: 2025
# Source: https://github.com/angelmtenor/ds-template
# Description: Builds a development container with Git, UV, Cookiecutter, and essential data science tools.
#              Optional GPU (NVIDIA/CUDA) support via build argument.
# Build Arguments:
#   - ENABLE_GPU: Set to "true" to enable NVIDIA/CUDA support (default: false)
#   - USERNAME: Non-root username (default: user)
#   - USER_UID: User ID (default: 1000)
#   - USER_GID: Group ID (default: 1000)

# Base image
FROM ubuntu:24.04

# Metadata
LABEL maintainer="Angel Martinez-Tenor <angelmtenor@gmail.com>" \
    version="2.0" \
    description="Data Science Dev Container with Git, UV, Cookiecutter, and optional GPU support"

# Build arguments
ARG ENABLE_GPU=false
ARG USERNAME=user
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    NEEDRESTART_MODE=a \
    SHELL=/bin/bash \
    PATH=/home/$USERNAME/.local/bin:$PATH

# Set system timezone to UTC
RUN rm -f /etc/localtime /etc/timezone && \
    echo "Etc/UTC" > /etc/timezone && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "tzdata tzdata/Areas select Etc" | debconf-set-selections && \
    echo "tzdata tzdata/Zones/Etc select UTC" | debconf-set-selections

# Install tini as init system for better signal handling
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Remove default ubuntu user and install system packages
RUN userdel -r ubuntu 2>/dev/null || true && \
    apt-get update -y && \
    apt-get full-upgrade -y && \
    apt-get install -y --no-install-recommends \
    git \
    git-flow \
    make \
    curl \
    wget \
    ca-certificates \
    nano \
    htop \
    gcc \
    g++ \
    clang \
    linux-libc-dev \
    pipx \
    xclip \
    python3 \
    python3-pip \
    python3-venv \
    unzip \
    zip \
    ffmpeg \
    libsm6 \
    libxext6 \
    sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Optional GPU support (NVIDIA/CUDA)
RUN if [ "$ENABLE_GPU" = "true" ]; then \
    apt-get update -y && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y ppa:graphics-drivers/ppa && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
    ubuntu-drivers-common \
    nvidia-driver-latest \
    nvidia-cuda-toolkit \
    nvtop && \
    ubuntu-drivers autoinstall || true && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*; \
    fi

# Create non-root user with minimal sudo privileges
RUN groupadd --gid "$USER_GID" "$USERNAME" && \
    useradd --uid "$USER_UID" --gid "$USER_GID" -m "$USERNAME" -s /bin/bash && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:/usr/bin/apt-get" > /etc/sudoers.d/"$USERNAME" && \
    chmod 0440 /etc/sudoers.d/"$USERNAME"

# Switch to non-root user
USER $USERNAME
WORKDIR /home/$USERNAME

# Install user-level tools (UV via curl, Cookiecutter via uv)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /home/$USERNAME/.local/bin/uv tool install cookiecutter && \
    /home/$USERNAME/.local/bin/uv tool ensurepath

# Install/update NVM and Node.js 20
ENV NVM_DIR=/home/$USERNAME/.nvm
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash \
    && . "$NVM_DIR/nvm.sh" \
    && nvm install 20 \
    && nvm alias default 20 \
    && nvm cache clear

# Make Node available in PATH for subsequent Dockerfile commands
ENV PATH=$NVM_DIR/versions/node/v20.*/bin:$PATH

# Configure Git
RUN git config --global init.defaultBranch main && \
    git config --global core.editor nano && \
    git config --global user.name "user" && \
    git config --global user.email "user@example.com"

# Configure shell (prompt, alias, PATH)
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> .bashrc && \
    echo 'export PS1="\[\e[32m\]\u@\h \[\e[34m\]\w\[\e[0m\]\$ "' >> .bashrc && \
    echo 'alias setup="source setup_user.sh"' >> .bashrc && \
    echo "source ~/.bashrc" >> .bash_profile

# Set entrypoint to use tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/bin/bash"]

# Suggest using the setup script with relative path
RUN echo "To set up or re-run your development environment, run the following command from your workspace directory:" && \
    echo "  source setup_user.sh" && \
    echo "You can also use the alias 'setup' (ensure you're in the correct directory)." && \
    echo "For more information, check the README.md file in the repository."
