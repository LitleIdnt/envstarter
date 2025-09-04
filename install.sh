#!/bin/bash

echo "EnvStarter Installation Script"
echo "============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found. Installing dependencies..."
echo

# Install dependencies
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Failed to install dependencies"
    echo "Try using sudo or check your internet connection"
    exit 1
fi

echo
echo "Running installation test..."
echo

python3 test_installation.py

if [ $? -ne 0 ]; then
    echo
    echo "Installation test failed. Please check the errors above."
    exit 1
fi

echo
echo "============================="
echo "Installation completed successfully!"
echo "============================="
echo
echo "To run EnvStarter:"
echo "  python3 -m src.envstarter.main"
echo
echo "Or use the run script: ./run_envstarter.sh"
echo

# Create run script
cat > run_envstarter.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 -m src.envstarter.main
EOF

chmod +x run_envstarter.sh

echo "Created run_envstarter.sh for easy launching."
echo