# 🚀 ENVSTARTER GUI APPLICATION GUIDE 🚀

## Starting the Main GUI App

### Windows:
```cmd
python EnvStarter.py
```
Or double-click `EnvStarter.py` if Python is associated with .py files

### Linux/Mac:
```bash
python3 EnvStarter.py
# OR
./EnvStarter.py
```

## Main GUI Features

### 1. 🎯 Environment Selector (Main Window)
When you run `EnvStarter.py`, you'll see:
- **Environment List**: All your configured environments
- **Launch Button**: Click to launch selected environment
- **Settings Button**: Configure environments
- **Dashboard Button**: View all running environments
- **Launch All Button**: Start ALL environments at once
- **Stop All Button**: Stop all running containers

### 2. ⚙️ Settings Dialog
Click "Settings" to:
- **Create New Environment**: 
  - Name your environment
  - Add applications (browse for .exe files)
  - Add websites (URLs to open)
  - Set startup delays
- **Edit Existing Environments**:
  - Modify applications
  - Change descriptions
  - Enable/disable items
- **Delete Environments**
- **Import/Export** environment configurations

### 3. 🎮 Multi-Environment Dashboard
Click "Dashboard" to see:
- **All Running Environments** in a grid view
- **Real-time Stats**: CPU, Memory, Process count
- **Quick Actions**: 
  - Switch to environment
  - Stop container
  - Pause/Resume
- **Resource Monitoring**: System-wide usage

### 4. 🔔 System Tray
- **Minimize to Tray**: App keeps running in background
- **Right-click Tray Icon** for:
  - Quick launch menu
  - Running containers list
  - Switch between environments
  - Open dashboard
  - Settings
  - Exit

## 🎯 NEW ISOLATION FEATURES IN GUI

When you launch an environment from the GUI:

1. **VM-Like Isolation**: Each environment runs in its own virtual desktop (Windows) or namespace (Linux)

2. **BIG VISIBLE HEADERS**: A massive floating header appears showing:
   ```
   ╔════════════════════════════════════════════════════════════╗
   ║     🚀 ENVIRONMENT: [YOUR ENV NAME] 🚀                     ║
   ║     Status: RUNNING | Apps: 5 | RAM: 250MB | CPU: 12%     ║
   ╚════════════════════════════════════════════════════════════╝
   ```

3. **Window Title Injection**: All applications show `[Environment Name] App Name`

4. **Environment Status Bar**: Shows all running environments at the top of the main window

## Quick Start Workflow

1. **Run the GUI**:
   ```bash
   python EnvStarter.py
   ```

2. **First Time Setup**:
   - Click "Settings"
   - Click "Add Environment"
   - Name it (e.g., "Work", "Gaming", "Development")
   - Add applications using "Browse" button
   - Add websites using "Add Website" button
   - Click "Save"

3. **Launch Environment**:
   - Select environment from list
   - Click "🚀 Launch Environment"
   - Watch the progress bar
   - See the BIG ENVIRONMENT HEADER appear!
   - Environment launches in isolated container

4. **Switch Between Environments**:
   - Use Dashboard to see all running
   - Click "Switch" to jump between them
   - Or use System Tray menu

5. **Stop Everything**:
   - Click "Stop All" in main window
   - Or right-click tray → Stop All Containers

## Keyboard Shortcuts

- **Ctrl+Enter**: Launch selected environment
- **Ctrl+,**: Open settings
- **Ctrl+M**: Minimize to tray
- **Ctrl+Q**: Quit application
- **Escape**: Minimize to tray

## Tips

- **Auto-start**: Enable in Settings → General → "Start with Windows"
- **Multiple Monitors**: Environments can span across all monitors
- **Resource Limits**: Dashboard shows when you're near limits
- **Quick Launch**: Double-click environment to launch immediately

## The GUI App is Your Control Center!

The GUI provides EVERYTHING you need:
- ✅ Create and manage environments
- ✅ Launch with visual feedback
- ✅ Monitor all running environments
- ✅ Switch between isolated containers
- ✅ See BIG HEADERS with environment names
- ✅ System tray for background operation

No command line needed - everything is in the GUI!