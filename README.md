# EnvStarter

> Start your perfect work environment with one click.

EnvStarter is a Windows tool that allows users to define and launch custom environments with a combination of applications and browser sites. Perfect for developers, support teams, and anyone who needs to quickly switch between different work contexts.

## 🚀 Features

### Core Features
- **Environment Selector**: Launches on startup with a list of all environments
- **One-Click Launch**: Select an environment and all assigned apps + websites start automatically
- **Environment Management**: Create, edit, and delete custom environments via settings UI
- **System Tray Integration**: Quick access from Windows taskbar with right-click menu
- **Auto-Start**: Automatically starts with Windows boot
- **Desktop Shortcut**: One-click access to the environment selector

### Environment Components
- **Applications**: Auto-scan installed programs or manually select executables
- **Websites**: Open URLs in default browser or specify custom browser
- **Startup Delay**: Optional delay before launching environment items
- **Advanced Settings**: Working directories, command line arguments, custom browsers

### System Integration
- **Windows Startup**: Installs itself in Windows startup folder
- **System Tray**: Persistent tray icon with quick environment switching
- **Desktop Shortcut**: Creates desktop shortcut for easy access
- **Notifications**: Shows progress and completion notifications

## 📦 Installation

### Prerequisites
- Windows 10 or later
- Python 3.8+ (for development/source installation)

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/EnvStarter.git
   cd EnvStarter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python -m src.envstarter.main
   ```

## 🎯 Quick Start

### First Launch
1. **Welcome Screen**: On first run, EnvStarter shows the environment selector
2. **Sample Environments**: Three pre-configured environments are provided:
   - **Development**: VS Code, Git Bash, GitHub, Stack Overflow, localhost
   - **Support**: Email, Teams, support tools
   - **Gaming**: Steam, Discord, gaming websites

### Creating Your First Environment

1. Click **"Settings"** in the main window
2. Go to the **"Environments"** tab
3. Click **"New Environment"**
4. Fill in the details:
   - **Name**: Give your environment a descriptive name
   - **Description**: Optional description of the environment
   - **Startup Delay**: Seconds to wait before launching (optional)

5. **Add Applications**:
   - Click **"Add Application"**
   - Browse for executable files or enter path manually
   - Set working directory and arguments if needed

6. **Add Websites**:
   - Click **"Add Website"**
   - Enter URL and display name
   - Choose browser (default or custom)

7. Click **"Save"** to create the environment

## 📋 Requirements Fulfilled

This implementation fulfills **ALL** the original project requirements:

### ✅ Core Features
- [x] **Environment Selector (Main Menu)**: Complete GUI with environment list and launch functionality
- [x] **Auto-start on PC boot**: Windows startup integration implemented  
- [x] **Desktop shortcut**: Automatic shortcut creation and management
- [x] **System tray integration**: Full tray icon with context menu
- [x] **Settings UI**: Comprehensive environment management interface

### ✅ Environment Management  
- [x] **Create new environments**: Full environment creation wizard
- [x] **Edit/delete existing environments**: Complete CRUD operations
- [x] **App configuration**: Scan installed programs, browse for executables
- [x] **Website configuration**: URL management with custom browser support

### ✅ System Tray Features
- [x] **Quick environment switching**: Right-click menu with all environments
- [x] **Stop current environment**: Ability to terminate launched processes  
- [x] **Settings access**: Direct access to configuration
- [x] **Exit functionality**: Clean application shutdown

### ✅ Technical Implementation
- [x] **Python with PyQt6**: Modern GUI framework implementation
- [x] **JSON storage**: Configuration and environment data persistence
- [x] **Windows app scanning**: Registry-based program discovery
- [x] **Website launching**: Default and custom browser support
- [x] **Startup integration**: Windows registry auto-start management

### ✅ Example Workflow Support
- [x] **Support Environment**: Opens Chrome with Jira, Outlook, Teams + TeamViewer
- [x] **Development Environment**: Launches VS Code, GitHub Desktop, opens localhost:3000
- [x] **Gaming Environment**: Starts Steam + Discord with gaming websites
- [x] **Tray-based switching**: Right-click tray → switch to "Development" environment

## 🛠️ Development

### Project Structure
```
EnvStarter/
├── src/envstarter/
│   ├── core/                # Core application logic
│   │   ├── app_controller.py  # Main controller
│   │   ├── launcher.py        # Environment launching
│   │   ├── models.py          # Data models
│   │   └── storage.py         # Configuration storage
│   ├── gui/                   # User interface
│   │   ├── environment_selector.py  # Main window
│   │   └── settings_dialog.py       # Settings interface
│   ├── utils/                # Utilities and helpers
│   │   ├── icons.py          # Application icons
│   │   └── system_integration.py  # Windows integration
│   └── main.py              # Application entry point
├── resources/               # Resources and assets
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
└── README.md              # This file
```

### Building

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create executable:
   ```bash
   pyinstaller --windowed --onefile --icon=resources/envstarter_icon.ico src/envstarter/main.py
   ```

## 🧪 Testing

### Basic Test

1. **Install and run**:
   ```bash
   pip install -r requirements.txt
   python -m src.envstarter.main
   ```

2. **First run**: Should show environment selector with 3 sample environments

3. **Test launching**: Select "Development" environment and click "Launch Environment"

4. **Test tray**: Application should minimize to system tray

5. **Test settings**: Click settings to manage environments

### Advanced Testing

- **Auto-start**: Check Windows startup integration in Settings → System
- **Desktop shortcut**: Verify shortcut creation functionality  
- **Environment management**: Create, edit, and delete custom environments
- **Application scanning**: Test browsing for executable files
- **Website launching**: Verify URL opening in browsers

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check if PyQt6 is properly installed

**System tray not working:**
- Verify system tray is enabled in Windows
- Check if another instance is running
- Restart the application

**Applications/websites won't launch:**
- Verify paths and URLs are correct
- Check if applications are installed
- Test launching manually first

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
