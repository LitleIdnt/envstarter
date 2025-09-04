# User Guide - EnvStarter

This comprehensive guide covers all features and functionality of EnvStarter.

## Getting Started

### First Launch

When you first run EnvStarter, you'll see the **Environment Selector** window with three pre-configured sample environments:

1. **Development** - VS Code, Git Bash, GitHub, Stack Overflow, localhost
2. **Support** - Email, Teams, support tools  
3. **Gaming** - Steam, Discord, gaming websites

### Basic Usage

1. **Select an Environment**: Click on any environment from the list
2. **View Details**: Environment details appear on the right panel
3. **Launch**: Click "Launch Environment" button
4. **Monitor Progress**: Watch the progress bar and launch log
5. **Minimize**: The window minimizes to system tray after successful launch

## Environment Management

### Creating New Environments

1. **Access Settings**: Click "Settings" button in main window
2. **Environments Tab**: Navigate to "Environments" tab
3. **New Environment**: Click "New Environment" button
4. **Fill Basic Info**:
   - **Name**: Give your environment a descriptive name
   - **Description**: Optional description of what this environment does
   - **Startup Delay**: Seconds to wait before launching items (0-300)

5. **Add Applications**:
   - Click "Add Application" button
   - **Name**: Display name for the application
   - **Path**: Browse for executable or type path manually
   - **Arguments**: Command line arguments (optional)
   - **Working Directory**: Starting directory for the application (optional)
   - **Wait for Exit**: Whether to wait for this app to close before continuing

6. **Add Websites**:
   - Click "Add Website" button  
   - **Name**: Display name for the website
   - **URL**: Full URL including http:// or https://
   - **Browser**: Use system default or specify custom browser
   - **New Tab**: Whether to open in new tab

7. **Save**: Click "Save" to create the environment

### Editing Environments

1. **Select Environment**: Choose environment from list in Settings → Environments
2. **Edit Button**: Click "Edit" button
3. **Modify Settings**: Change any environment properties
4. **Save Changes**: Click "Save" to apply changes

### Duplicating Environments

1. **Select Environment**: Choose environment to copy
2. **Duplicate Button**: Click "Duplicate" button  
3. **Modify Copy**: Edit the duplicated environment as needed
4. **Save**: Environment is saved with "(Copy)" appended to name

### Deleting Environments

1. **Select Environment**: Choose environment to delete
2. **Delete Button**: Click "Delete" button
3. **Confirm**: Confirm deletion in popup dialog
4. **Permanent**: Deletion cannot be undone

## Application Configuration

### Finding Applications

**Automatic Discovery**: EnvStarter can find installed applications by:
- Scanning Windows registry for installed programs
- Checking common installation directories
- Looking in Program Files and Program Files (x86)

**Manual Selection**: 
- Browse button opens file dialog
- Navigate to application executable (.exe, .msi, .bat, .cmd)
- Select the main executable file

### Application Settings

**Path Examples**:
```
C:\Program Files\Microsoft VS Code\Code.exe
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
notepad.exe  (for built-in Windows applications)
%USERPROFILE%\AppData\Local\Discord\app-1.0.9011\Discord.exe
```

**Arguments Examples**:
```
Chrome: --new-window --incognito
VS Code: --new-window C:\Projects\MyProject
Git Bash: --cd="C:\Projects"
Steam: -silent
```

**Working Directory Examples**:
```
C:\Projects\CurrentProject
%USERPROFILE%\Documents
D:\WorkSpace
```

### Advanced Application Features

**Wait for Exit**: 
- Enable this for applications that must complete before continuing
- Useful for installers, batch scripts, or sequential operations
- Most applications should leave this unchecked

**Environment Variables**:
- Paths can include Windows environment variables
- `%USERPROFILE%` expands to user home directory
- `%APPDATA%` expands to application data directory
- `%PROGRAMFILES%` expands to Program Files directory

## Website Configuration

### Basic Website Setup

**URL Requirements**:
- Must include protocol: `https://` or `http://`
- Can include ports: `http://localhost:3000`
- Can include paths: `https://github.com/myuser/myrepo`
- Can include parameters: `https://site.com?param=value`

**Examples**:
```
https://github.com
https://stackoverflow.com
https://mail.google.com
http://localhost:3000
https://teams.microsoft.com
```

### Browser Selection

**System Default**: 
- Uses Windows default browser
- Respects user's browser preferences
- Most common choice

**Custom Browser**:
- Specify path to specific browser executable
- Useful for testing in different browsers
- Can use different browser for different sites

**Browser Examples**:
```
Chrome: C:\Program Files\Google\Chrome\Application\chrome.exe
Firefox: C:\Program Files\Mozilla Firefox\firefox.exe
Edge: C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

### Website Launch Options

**New Tab vs New Window**:
- **New Tab**: Opens in existing browser window (recommended)
- **New Window**: Opens in separate browser window
- Behavior depends on browser configuration

## System Tray Features

### Tray Icon Functions

**Double-Click**: Opens main environment selector window

**Right-Click Menu**:
- **Show EnvStarter**: Open main window
- **Launch Environment**: Quick access to all environments
- **Stop Current**: Terminate currently launching environment
- **Settings**: Open settings dialog
- **Exit**: Close EnvStarter completely

### Quick Environment Switching

1. **Right-click** tray icon
2. **Navigate** to "Launch Environment"
3. **Select** desired environment from submenu
4. **Environment launches** automatically

This allows switching between environments without opening the main window.

### Tray Notifications

EnvStarter shows system notifications for:
- **Launch Started**: "Launching Development..."
- **Launch Completed**: "Development launched successfully!"
- **Launch Failed**: "Failed to launch Development"
- **Item Errors**: "Error launching Visual Studio Code"

## System Integration

### Windows Startup

**Automatic Setup**: 
- EnvStarter adds itself to Windows startup on first run
- Starts minimized to system tray
- No splash screen or main window shown

**Manual Control**:
- Settings → System → "Start with Windows"
- Toggle to enable/disable auto-start
- Changes take effect immediately

**Technical Details**:
- Adds registry entry to `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- Safe and standard Windows integration method
- Can be removed by unchecking the setting

### Desktop Shortcut

**Automatic Creation**: 
- Desktop shortcut created on first run
- Points to EnvStarter executable or Python script
- Standard Windows LNK file

**Manual Management**:
- Settings → System → "Create Shortcut" / "Remove Shortcut"
- Can create/remove shortcut at any time
- Handles both user and public desktop locations

## Advanced Features

### Environment Startup Delays

**Purpose**: 
- Prevent system overload when launching many applications
- Allow applications to start in sequence
- Useful for resource-heavy environments

**Configuration**:
- Set delay in seconds (0-300)
- Applies before launching any items in the environment
- Shows countdown in launch progress

**Use Cases**:
```
Heavy Development: 10 seconds
  - Docker Desktop (needs time to start)
  - Visual Studio (resource heavy)  
  - Multiple browsers with many tabs

Light Support: 0 seconds
  - Just email and chat applications
  - Quick startup needed
```

### Launch Progress Monitoring

**Progress Bar**: Shows overall launch progress (0-100%)

**Status Messages**: 
- "Starting Visual Studio Code..."
- "Opening GitHub..."
- "Launch completed!"

**Launch Log**: 
- ✓ Successfully launched items (green)
- ✗ Failed items (red)
- Detailed error messages

**Process Control**: 
- "Stop Current" button during launch
- Terminates all launched processes
- Useful if launch needs to be canceled

### Environment Validation

EnvStarter validates environments to ensure they work properly:

**Application Validation**:
- Checks if executable file exists
- Verifies file is actually executable
- Warns about missing applications

**Website Validation**:  
- Checks URL format (must start with http:// or https://)
- Validates basic URL structure
- Warns about malformed URLs

**Environment Validation**:
- Ensures environment has at least one item
- Checks for duplicate names
- Validates all settings before saving

## Troubleshooting

### Common Launch Issues

**Application Won't Start**:
1. Verify the path is correct
2. Check if application is installed
3. Try running the application manually
4. Check for missing dependencies
5. Verify user has permission to run the application

**Website Won't Open**:
1. Verify URL is correct and accessible
2. Check internet connection
3. Try opening URL manually in browser
4. Verify default browser is set correctly

**EnvStarter Won't Start**:
1. Check if already running in system tray
2. Restart Windows Explorer
3. Check Windows Event Viewer for errors
4. Verify PyQt6 is installed correctly

### Performance Optimization

**Large Environments**:
- Use startup delays for resource-heavy applications
- Stagger application launches by grouping in separate environments
- Monitor system resources during launch

**System Resources**:
- Close unnecessary applications before launching environments
- Ensure sufficient RAM for all applications
- Use SSD for better application startup times

### Configuration Issues

**Settings Not Saved**:
- Check write permissions to %APPDATA%\EnvStarter
- Verify disk space availability
- Check for antivirus blocking file writes

**Environments Disappeared**:
- Check %APPDATA%\EnvStarter\environments.json exists
- Verify file is not corrupted (should be valid JSON)
- Check for recent Windows updates or profile changes

## Tips and Best Practices

### Environment Organization

**By Role**:
- Development
- Testing  
- Support
- Management
- Personal

**By Project**:
- Project A Development
- Project A Testing
- Project B Development  
- Project B Testing

**By Time**:
- Morning Routine
- Afternoon Focus
- End of Day Cleanup

### Application Selection

**Essential Applications**:
- Include applications you always need together
- Don't include applications you sometimes skip
- Consider startup time and resource usage

**Website Selection**:
- Include frequently accessed sites
- Group related websites together
- Consider using bookmarks for less frequent sites

### Performance Tips

**Optimize Launch Times**:
- Place frequently used environments first in the list
- Use startup delays only when necessary
- Group lightweight applications together

**System Resources**:
- Monitor CPU and memory usage during launches
- Close unused applications before launching environments
- Consider upgrading RAM if launching large environments

### Maintenance

**Regular Cleanup**:
- Remove unused environments
- Update application paths when software is updated
- Verify URLs still work correctly

**Backup Configuration**:
- Copy %APPDATA%\EnvStarter folder for backup
- Export/import feature coming in future versions
- Document your environments for team sharing