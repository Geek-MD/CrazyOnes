#!/bin/bash
# CrazyOnes Setup Script
# This script helps automate the installation of Python dependencies

set -e  # Exit on error

# Handle Ctrl+C gracefully
trap 'echo ""; echo "Setup cancelled by user."; exit 130' INT

echo "=========================================="
echo "CrazyOnes Setup Script"
echo "=========================================="
echo ""

# Check if Python 3.10+ is installed
echo "Checking Python version..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "✗ Error: python3 is not installed"
    echo ""
    echo "Please install Python 3.10 or higher first:"
    echo "  - Debian/Ubuntu/Raspberry Pi OS: sudo apt install python3 python3-pip"
    echo "  - Fedora/RHEL/CentOS: sudo dnf install python3 python3-pip"
    echo "  - macOS: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"

# Check if Python version is 3.10 or higher
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "✗ Error: Python 3.10 or higher is required"
    echo "  Current version: $PYTHON_VERSION"
    exit 1
fi

echo ""

# Check if pip is installed
echo "Checking pip..."
if ! command -v pip3 >/dev/null 2>&1 && ! python3 -m pip --version >/dev/null 2>&1; then
    echo "✗ Error: pip is not installed"
    echo ""
    echo "Please install pip first:"
    echo "  - Debian/Ubuntu/Raspberry Pi OS: sudo apt install python3-pip"
    echo "  - Fedora/RHEL/CentOS: sudo dnf install python3-pip"
    echo "  - macOS: python3 -m ensurepip --upgrade"
    exit 1
fi

echo "✓ pip found"
echo ""

# Ask user if they want to use a virtual environment
echo "=========================================="
echo "Installation Method"
echo "=========================================="
echo ""
echo "You can install CrazyOnes dependencies in two ways:"
echo ""
echo "  1. System-wide installation (simpler, may require sudo)"
echo "  2. Virtual environment (recommended for development)"
echo ""

while true; do
    read -r -p "Choose installation method (1 or 2): " choice || {
        echo ""
        echo "Setup cancelled."
        exit 130
    }
    case $choice in
        1)
            USE_VENV=false
            break
            ;;
        2)
            USE_VENV=true
            break
            ;;
        *)
            echo "Invalid choice. Please enter 1 or 2."
            ;;
    esac
done

echo ""

# Install dependencies
if [ "$USE_VENV" = true ]; then
    echo "=========================================="
    echo "Creating Virtual Environment"
    echo "=========================================="
    echo ""
    
    # Create virtual environment
    if [ -d "venv" ]; then
        echo "⚠ Warning: venv directory already exists"
        read -r -p "Remove existing venv and create a new one? (y/n): " confirm || {
            echo ""
            echo "Setup cancelled."
            exit 130
        }
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            rm -rf venv
            echo "✓ Removed existing venv"
        else
            echo "Keeping existing venv"
        fi
    fi
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo "✓ Virtual environment created"
    fi
    
    echo ""
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo ""
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
    echo "✓ Dependencies installed in virtual environment"
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "To use CrazyOnes, you need to activate the virtual environment:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Then you can run:"
    echo "  python crazyones.py"
    echo ""
    echo "To deactivate the virtual environment later:"
    echo "  deactivate"
    echo ""
else
    echo "=========================================="
    echo "Installing Dependencies"
    echo "=========================================="
    echo ""
    echo "Installing dependencies system-wide..."
    
    # Try with user install first (no sudo)
    echo "Attempting user installation (no sudo required)..."
    if pip3 install --user -r requirements.txt || python3 -m pip install --user -r requirements.txt; then
        echo ""
        echo "✓ Dependencies installed (user install)"
    else
        echo ""
        echo "⚠ User install failed. Trying with sudo..."
        echo "You may be prompted for your password."
        echo ""
        if sudo pip3 install -r requirements.txt || sudo python3 -m pip install -r requirements.txt; then
            echo ""
            echo "✓ Dependencies installed (system-wide)"
        else
            echo ""
            echo "✗ Error: Failed to install dependencies"
            echo "Please check the error messages above for details."
            exit 1
        fi
    fi
    
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "You can now run CrazyOnes:"
    echo "  python3 crazyones.py"
    echo ""
fi

# Offer to run configuration wizard
echo "Would you like to run the configuration wizard now?"
echo "This will help you set up your Telegram bot token and optionally"
echo "install CrazyOnes as a systemd service."
echo ""

read -r -p "Run configuration wizard? (y/n): " run_config || {
    echo ""
    echo "Skipping configuration wizard."
    run_config="n"
}

if [ "$run_config" = "y" ] || [ "$run_config" = "Y" ]; then
    echo ""
    echo "Starting configuration wizard..."
    echo ""
    if [ "$USE_VENV" = true ]; then
        python crazyones.py --config
    else
        python3 crazyones.py --config
    fi
else
    echo ""
    echo "You can run the configuration wizard later with:"
    echo "  python crazyones.py --config"
    echo ""
fi
