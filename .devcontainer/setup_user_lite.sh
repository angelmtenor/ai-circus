#!/bin/bash
# Minimal User Environment Setup (unguided)
# Usage: source setup_user.sh

set -e

BASHRC="$HOME/.bashrc"
LOCAL_BIN="$HOME/.local/bin"
NVM_DIR="$HOME/.nvm"

GREEN='\033[0;32m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
log(){ echo -e "${GREEN}✓ $1${NC}"; }
info(){ echo -e "${BLUE}ℹ $1${NC}"; }
err(){ echo -e "${RED}✗ $1${NC}"; exit 1; }

# Append a block to .bashrc if missing
append() {
    local tag="$1" text="$2"
    grep -qF "$tag" "$BASHRC" || { echo -e "$tag\n$text" >> "$BASHRC"; log "Added: $tag"; }
}

# Ensure ~/.local/bin is in PATH
ensure_path() {
    append "# PATH from setup_user" 'export PATH="$HOME/.local/bin:$PATH"'
    export PATH="$LOCAL_BIN:$PATH"
    log "PATH ensured."
}

# Configure Git basics automatically if missing
configure_git() {
    command -v git &>/dev/null || err "Git missing."

    git config --global init.defaultBranch main

    git config --global user.name  >/dev/null || git config --global user.name  "user"
    git config --global user.email >/dev/null || git config --global user.email "user@example.com"

    log "Git configured."
}

# Simple prompt
set_prompt() {
    append "# prompt from setup_user" 'export PS1="\[\e[32m\]\u@\h \[\e[34m\]\w\[\e[0m\]\$ "'
    log "Prompt set."
}

# Add alias
add_alias() {
    append "# alias from setup_user" 'alias setup="source setup.sh"'
    log "Alias added."
}

# Install/update nvm + Node 20
install_nvm() {
    local latest=$(curl -s https://api.github.com/repos/nvm-sh/nvm/releases/latest | grep tag_name | cut -d'"' -f4)

    # Install/update nvm
    curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/$latest/install.sh" | bash >/dev/null 2>&1
    . "$NVM_DIR/nvm.sh"

    # Ensure Node 20
    nvm install 20 --latest-npm >/dev/null 2>&1
    nvm alias default 20
    log "nvm + Node 20 ready."
}

# Install/update uv
install_uv() {
    curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
    log "uv installed/updated."
}

main() {
    command -v curl &>/dev/null || err "curl missing."

    log "Starting user setup..."
    ensure_path
    configure_git
    set_prompt
    add_alias
    install_nvm
    install_uv

    log "Setup complete. Run: source ~/.bashrc"
}

main
