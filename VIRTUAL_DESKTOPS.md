# 🖥️ EnvStarter Virtual Desktop Integration

## Overview

EnvStarter now supports **Windows Virtual Desktops** to create completely isolated work environments that act like separate VMs. Each environment can run on its own virtual desktop, providing perfect separation between different workflows.

## 🎯 What Are Virtual Desktops?

Virtual Desktops are Windows 10/11's built-in feature that allows you to create multiple desktop spaces. Think of them as **separate computer screens** where:

- ✅ Each desktop has its own taskbar and running applications
- ✅ Applications are completely isolated from other desktops  
- ✅ You can switch between desktops instantly
- ✅ Perfect for separating Work, Gaming, Development, etc.

## 🚀 How EnvStarter Uses Virtual Desktops

### Environment Isolation
Each EnvStarter environment can:
- **Launch on a dedicated virtual desktop**
- **Auto-switch to that desktop when started**
- **Keep all applications contained** on that desktop
- **Close all applications when stopped** (optional)

### Like Having Multiple VMs
- **Support Environment** → Desktop 1 (Teams, Outlook, Support tools)
- **Development Environment** → Desktop 2 (VSCode, browsers, dev tools)  
- **Gaming Environment** → Desktop 3 (Steam, Discord, game launchers)
- **Personal Environment** → Desktop 4 (Social media, entertainment)

## ⚙️ Configuration Options

### Environment Settings

```json
{
  "name": "Development",
  "use_virtual_desktop": true,        // Enable virtual desktop isolation
  "desktop_index": 2,                 // Use specific desktop (1-10)
  "desktop_name": "DevWork",          // Custom desktop name
  "auto_switch_desktop": true,        // Switch to this desktop on launch
  "close_apps_on_stop": true          // Close all apps when stopping
}
```

### Configuration Explained

| Setting | Description | Default |
|---------|-------------|---------|
| `use_virtual_desktop` | Enable/disable virtual desktop isolation | `true` |
| `desktop_index` | Specific desktop number (1-10), -1 = auto-assign | `-1` (auto) |
| `desktop_name` | Custom name for the desktop | `"EnvStarter-{Environment}"` |
| `auto_switch_desktop` | Switch to desktop when launching | `true` |
| `close_apps_on_stop` | Close apps when stopping environment | `false` |

## 🎮 Usage Examples

### Example 1: Work Environment
```json
{
  "name": "Work",
  "use_virtual_desktop": true,
  "desktop_index": 1,
  "desktop_name": "Work-Desktop",
  "auto_switch_desktop": true,
  "close_apps_on_stop": false,
  "applications": [
    {"name": "Microsoft Teams", "path": "shell:appsFolder\\Microsoft.Teams_xyz"},
    {"name": "Outlook", "path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"}
  ],
  "websites": [
    {"name": "Company Portal", "url": "https://portal.company.com"}
  ]
}
```

**Result:** All work apps launch on Desktop 1, completely isolated from personal stuff

### Example 2: Gaming Setup  
```json
{
  "name": "Gaming",
  "use_virtual_desktop": true,
  "desktop_index": 3,
  "desktop_name": "Gaming-Zone",
  "auto_switch_desktop": true,
  "close_apps_on_stop": true,
  "applications": [
    {"name": "Steam", "path": "C:\\Program Files (x86)\\Steam\\steam.exe"},
    {"name": "Discord", "path": "C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\app-1.0.0\\Discord.exe"}
  ]
}
```

**Result:** Gaming desktop with all games and chat, auto-closes when done

### Example 3: Development Environment
```json
{
  "name": "Development", 
  "use_virtual_desktop": true,
  "desktop_index": 2,
  "auto_switch_desktop": true,
  "applications": [
    {"name": "VSCode", "path": "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"},
    {"name": "Git Bash", "path": "C:\\Program Files\\Git\\git-bash.exe"}
  ],
  "websites": [
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com"}
  ]
}
```

**Result:** Dedicated development workspace with all coding tools

## 🔧 Manual Desktop Controls

### Keyboard Shortcuts
- **Win + Ctrl + D** - Create new virtual desktop
- **Win + Ctrl + Left/Right** - Switch between desktops  
- **Win + Ctrl + F4** - Close current virtual desktop
- **Win + Tab** - View all desktops and switch

### EnvStarter Integration
EnvStarter automatically handles:
- ✅ Desktop creation
- ✅ Desktop switching  
- ✅ Application launching on correct desktop
- ✅ Environment cleanup (optional)

## 🎯 Benefits Over Regular Environments

### Without Virtual Desktops
```
Desktop 1: Teams + VSCode + Steam + Browser + Outlook + Discord
❌ Everything mixed together
❌ Alt+Tab shows ALL applications  
❌ Taskbar cluttered with everything
❌ Hard to focus on specific work
```

### With Virtual Desktops
```
Desktop 1: Teams + Outlook           (Work)
Desktop 2: VSCode + Browser          (Development) 
Desktop 3: Steam + Discord           (Gaming)
✅ Perfect separation
✅ Clean taskbars per environment
✅ Focus on current task only
✅ Switch environments instantly
```

## 💡 Advanced Features

### Auto-Assignment
If `desktop_index: -1`, EnvStarter automatically assigns desktops based on environment name:
- Same environment name = same desktop
- Different environments = different desktops
- Up to 10 environments supported

### Environment Cleanup
With `close_apps_on_stop: true`:
- Stopping environment closes ALL applications on that desktop
- Perfect for temporary setups (gaming, testing, etc.)
- Keeps system clean

### Desktop Persistence
Virtual desktops persist across:
- ✅ EnvStarter restarts
- ✅ Application crashes
- ✅ System reboots (Windows 11)
- ✅ Multiple environment launches

## 🛠️ Troubleshooting

### Virtual Desktop Not Working?
1. **Check Windows Version**: Requires Windows 10 v1903+ or Windows 11
2. **Enable Virtual Desktops**: Settings > System > Multitasking > Virtual Desktops
3. **Try Manual Creation**: Win+Ctrl+D to create desktop manually
4. **Check EnvStarter Logs**: Look for virtual desktop errors

### Applications Not Switching?
- Some applications may not respect virtual desktop boundaries
- Windows Store apps work better than legacy applications
- Try enabling `auto_switch_desktop: true`

### Desktop Switching Slow?
- Add small delays between application launches
- Increase `startup_delay` in environment settings
- Close unnecessary background applications

## 🎉 Best Practices

### 1. Environment Organization
```
Desktop 1: Main/Personal
Desktop 2: Work/Office  
Desktop 3: Development/Coding
Desktop 4: Gaming/Entertainment
Desktop 5: Testing/Temporary
```

### 2. Naming Convention
Use descriptive desktop names:
- ✅ `"Work-Support"`
- ✅ `"Dev-WebApp"`  
- ✅ `"Gaming-Steam"`
- ❌ `"Desktop1"`

### 3. Application Cleanup
Enable `close_apps_on_stop` for:
- ✅ Gaming environments
- ✅ Testing environments
- ✅ Temporary setups
- ❌ Work environments (keep documents open)

### 4. Resource Management
- Limit to 4-5 active desktops
- Close unused environments
- Monitor system resources

## 🔮 Future Enhancements

- **Desktop Wallpapers**: Custom wallpaper per environment
- **Desktop Icons**: Show only relevant shortcuts per desktop
- **Performance Monitoring**: Track resource usage per desktop
- **Desktop Backups**: Save/restore desktop layouts
- **Multi-Monitor**: Support for multi-monitor virtual desktops

## 🆘 Need Help?

Virtual Desktop issues? Check:
1. **Windows Settings** > System > Multitasking
2. **Task Manager** > More details > Process tab
3. **EnvStarter Logs** in %APPDATA%\\EnvStarter\\logs
4. **GitHub Issues** for community support

---

**🎯 Ready to separate your workflows like a pro? Enable Virtual Desktops and experience true environment isolation!**