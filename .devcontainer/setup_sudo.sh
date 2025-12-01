#!/bin/bash
#
# Ubuntu 24.04 Simple Setup Script
#
# Usage:
#   chmod +x setup_sudo.sh
#   sudo ./setup_sudo.sh [--gpu]
#
# Parameters:
#   --gpu
#       Optional. Installs NVIDIA GPU support by:
#         • Adding the graphics-drivers PPA
#         • Installing the latest NVIDIA driver
#         • Installing CUDA toolkit and utilities (e.g., nvtop)
#       A reboot is recommended when using this flag.
#
# Description:
#   This script performs a streamlined, non-interactive initial setup for
#   Ubuntu 24.04 systems. It:
#     • Ensures execution as root
#     • Sets system timezone to UTC
#     • Checks for internet connectivity
#     • Updates and upgrades the system
#     • Installs a curated set of development and utility packages
#     • Optionally configures GPU driver and CUDA support
#     • Performs basic post-installation verification
#
# Notes:
#   - Must be run with sudo or as root.
#   - Designed to be simple, readable, and easy to modify.
#   - Safe to re-run; package installation is idempotent.


set -e

# --- Colors ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log(){ echo -e "$2${1}${NC}"; }

# --- Must run as root ---
[[ $EUID -ne 0 ]] && { log "${RED}❌ Run as root"; exit 1; }

export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a

# Force UTC timezone and pre-seed tzdata
rm -f /etc/localtime /etc/timezone
echo "Etc/UTC" > /etc/timezone
ln -fs /usr/share/zoneinfo/UTC /etc/localtime
debconf-set-selections <<EOF
tzdata tzdata/Areas select Etc
tzdata tzdata/Zones/Etc select UTC
EOF

# --- Check internet ---
wget -q --spider http://google.com || { log "${RED}❌ No internet detected"; exit 2; }

# --- Package list (easy to edit) ---
PACKAGES=(
  git git-flow make curl wget ca-certificates
  nano htop gcc g++ clang linux-libc-dev pipx xclip
  python3 python3-pip python3-venv
)

log "${GREEN}ℹ️ Updating system..."
apt update -y && apt full-upgrade -y

log "${GREEN}ℹ️ Installing base packages..."
apt install -y --no-install-recommends "${PACKAGES[@]}"
apt autoremove -y

# --- Optional GPU setup ---
if [[ $1 == "--gpu" ]]; then
    log "${YELLOW}⚡ GPU flag detected: installing NVIDIA/CUDA..."

    apt install -y software-properties-common
    add-apt-repository -y ppa:graphics-drivers/ppa
    apt update -y

    apt install -y \
        ubuntu-drivers-common nvidia-driver-latest \
        nvidia-cuda-toolkit nvtop

    ubuntu-drivers autoinstall || true

    log "${GREEN}✅ NVIDIA/CUDA installed. Reboot recommended."
fi

# --- Verification (minimal) ---
for cmd in git curl gcc python3; do
    command -v "$cmd" &>/dev/null || { log "${RED}❌ $cmd missing."; exit 3; }
done

log "${GREEN}✅ Setup complete!"
[[ $1 == "--gpu" ]] && log "${YELLOW}⚠️ Reboot required for GPU drivers."
