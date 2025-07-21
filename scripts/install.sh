"""
Installation script for NMAP-AI on Linux/macOS systems.
"""

#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/nmap-ai"
BIN_DIR="/usr/local/bin"
PYTHON_MIN_VERSION="3.8"
NMAP_MIN_VERSION="7.0"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "Python $python_version found, but Python $PYTHON_MIN_VERSION or higher is required"
        exit 1
    fi
    log_success "Python $python_version found"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_warning "pip3 not found, attempting to install..."
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            yum install -y python3-pip
        elif command -v brew &> /dev/null; then
            brew install python3
        else
            log_error "Cannot install pip3. Please install it manually."
            exit 1
        fi
    fi
    log_success "pip3 found"
    
    # Check nmap
    if ! command -v nmap &> /dev/null; then
        log_warning "nmap not found, attempting to install..."
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y nmap
        elif command -v yum &> /dev/null; then
            yum install -y nmap
        elif command -v brew &> /dev/null; then
            brew install nmap
        else
            log_error "Cannot install nmap. Please install it manually."
            exit 1
        fi
    fi
    
    nmap_version=$(nmap --version | head -n1 | grep -oE '[0-9]+\.[0-9]+')
    log_success "nmap $nmap_version found"
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_warning "git not found, attempting to install..."
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y git
        elif command -v yum &> /dev/null; then
            yum install -y git
        elif command -v brew &> /dev/null; then
            brew install git
        else
            log_error "Cannot install git. Please install it manually."
            exit 1
        fi
    fi
    log_success "git found"
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y python3-dev python3-venv build-essential libssl-dev libffi-dev
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum groupinstall -y "Development Tools"
        yum install -y python3-devel openssl-devel libffi-devel
    elif command -v brew &> /dev/null; then
        # macOS
        brew install openssl libffi
    fi
    
    log_success "System dependencies installed"
}

# Download and install NMAP-AI
install_nmap_ai() {
    log_info "Installing NMAP-AI..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Clone repository
    if [ -d ".git" ]; then
        log_info "Updating existing installation..."
        git pull origin main
    else
        log_info "Cloning NMAP-AI repository..."
        git clone https://github.com/yashab-cyber/nmap-ai.git .
    fi
    
    # Create virtual environment
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install development dependencies if requested
    if [ "$1" = "--dev" ]; then
        log_info "Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi
    
    # Initialize AI models and databases
    log_info "Initializing AI models and databases..."
    python -m nmap_ai.setup --init-models --init-db
    
    log_success "NMAP-AI installed successfully"
}

# Create system binaries
create_binaries() {
    log_info "Creating system binaries..."
    
    # Create nmap-ai command
    cat > "$BIN_DIR/nmap-ai" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python -m nmap_ai "\$@"
EOF
    
    # Create nmap-ai-gui command
    cat > "$BIN_DIR/nmap-ai-gui" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python -m nmap_ai --gui
EOF
    
    # Create nmap-ai-web command
    cat > "$BIN_DIR/nmap-ai-web" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python -m nmap_ai --web "\$@"
EOF
    
    # Make binaries executable
    chmod +x "$BIN_DIR/nmap-ai"
    chmod +x "$BIN_DIR/nmap-ai-gui"
    chmod +x "$BIN_DIR/nmap-ai-web"
    
    log_success "System binaries created"
}

# Create desktop entry for GUI
create_desktop_entry() {
    if command -v desktop-file-install &> /dev/null; then
        log_info "Creating desktop entry..."
        
        cat > /tmp/nmap-ai.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NMAP-AI
Comment=AI-Powered Network Scanning Tool
Exec=$BIN_DIR/nmap-ai-gui
Icon=$INSTALL_DIR/assets/icons/nmap-ai.png
Terminal=false
StartupNotify=true
Categories=Network;Security;
Keywords=nmap;network;security;scanning;ai;
EOF
        
        desktop-file-install /tmp/nmap-ai.desktop
        rm /tmp/nmap-ai.desktop
        
        log_success "Desktop entry created"
    fi
}

# Set up systemd service (optional)
setup_service() {
    if command -v systemctl &> /dev/null && [ "$1" = "--service" ]; then
        log_info "Setting up systemd service..."
        
        cat > /etc/systemd/system/nmap-ai-web.service << EOF
[Unit]
Description=NMAP-AI Web Service
After=network.target

[Service]
Type=simple
User=nmap-ai
WorkingDirectory=$INSTALL_DIR
ExecStart=$BIN_DIR/nmap-ai-web --host 0.0.0.0 --port 8080
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
        
        # Create service user
        if ! id "nmap-ai" &>/dev/null; then
            useradd -r -s /bin/false nmap-ai
            chown -R nmap-ai:nmap-ai "$INSTALL_DIR"
        fi
        
        systemctl daemon-reload
        systemctl enable nmap-ai-web.service
        
        log_success "Systemd service configured"
        log_info "Start the service with: systemctl start nmap-ai-web"
    fi
}

# Clean up temporary files
cleanup() {
    log_info "Cleaning up temporary files..."
    
    # Remove any temporary files
    rm -f /tmp/nmap-ai-install.log
    
    log_success "Cleanup completed"
}

# Main installation function
main() {
    echo "=========================================="
    echo "       NMAP-AI Installation Script       "
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    INSTALL_DEV=false
    INSTALL_SERVICE=false
    
    for arg in "$@"; do
        case $arg in
            --dev)
                INSTALL_DEV=true
                ;;
            --service)
                INSTALL_SERVICE=true
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --dev       Install development dependencies"
                echo "  --service   Set up systemd service for web interface"
                echo "  --help      Show this help message"
                echo ""
                exit 0
                ;;
        esac
    done
    
    # Check if running as root
    check_root
    
    # Install steps
    check_requirements
    install_system_deps
    
    if [ "$INSTALL_DEV" = true ]; then
        install_nmap_ai --dev
    else
        install_nmap_ai
    fi
    
    create_binaries
    create_desktop_entry
    
    if [ "$INSTALL_SERVICE" = true ]; then
        setup_service --service
    fi
    
    cleanup
    
    echo ""
    echo "=========================================="
    echo "     NMAP-AI Installation Complete!      "
    echo "=========================================="
    echo ""
    echo "Usage:"
    echo "  nmap-ai --help          # Show CLI help"
    echo "  nmap-ai-gui             # Launch GUI"
    echo "  nmap-ai-web             # Launch web interface"
    echo ""
    echo "Configuration:"
    echo "  Config files: $INSTALL_DIR/config/"
    echo "  Data files:   $INSTALL_DIR/data/"
    echo "  Logs:         $INSTALL_DIR/logs/"
    echo ""
    echo "For support, visit: https://github.com/yashab-cyber/nmap-ai"
    echo ""
}

# Run main function with all arguments
main "$@"
