#!/bin/bash

# 🚀 ENVSTARTER ISOLATED LAUNCHER 🚀
# Creates completely isolated environments like VMs!
# Each environment has a BIG VISIBLE NAME in the header!

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║         🚀 ENVSTARTER - ISOLATED ENVIRONMENT LAUNCHER 🚀                  ║"
echo "║                                                                            ║"
echo "║     Each environment runs in COMPLETE ISOLATION like a VM!                ║"
echo "║     Environment names are shown in BIG HEADERS everywhere!                ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "isolated_launcher.py" ]; then
    echo "❌ isolated_launcher.py not found. Please run this script from the EnvStarter directory."
    exit 1
fi

# Parse arguments
ENVIRONMENT=""
MONITOR=false
LIST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --list|-l)
            LIST=true
            shift
            ;;
        --monitor|-m)
            MONITOR=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [environment_name] [options]"
            echo ""
            echo "Options:"
            echo "  --list, -l      List all available environments"
            echo "  --monitor, -m   Keep monitoring after launch"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Interactive mode"
            echo "  $0 'Work'             # Launch 'Work' environment"
            echo "  $0 all                # Launch ALL environments"
            echo "  $0 --list            # List available environments"
            echo "  $0 'Work' --monitor  # Launch and monitor 'Work' environment"
            exit 0
            ;;
        *)
            ENVIRONMENT="$1"
            shift
            ;;
    esac
done

# List environments if requested
if [ "$LIST" = true ]; then
    echo "📋 Listing available environments..."
    python3 isolated_launcher.py --list
    exit 0
fi

# Launch environment
if [ -n "$ENVIRONMENT" ]; then
    echo "🚀 Launching environment: $ENVIRONMENT"
    echo ""
    
    if [ "$MONITOR" = true ]; then
        python3 isolated_launcher.py "$ENVIRONMENT" --monitor
    else
        python3 isolated_launcher.py "$ENVIRONMENT"
    fi
else
    # Interactive mode
    echo "📋 Available environments:"
    python3 isolated_launcher.py --list
    echo ""
    echo "Enter environment name to launch (or 'all' for all environments):"
    read -r env_name
    
    if [ -n "$env_name" ]; then
        echo ""
        echo "🚀 Launching environment: $env_name"
        
        if [ "$MONITOR" = true ]; then
            python3 isolated_launcher.py "$env_name" --monitor
        else
            python3 isolated_launcher.py "$env_name"
        fi
    else
        echo "❌ No environment specified"
        exit 1
    fi
fi