# Technical Specifications - EnvStarter

## Architecture Overview

EnvStarter is built using a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│                 Main App                    │
│            (main.py)                        │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│            App Controller                   │
│         (app_controller.py)                 │
├─────────────┬───────────┬───────────────────┤
│   Storage   │ Launcher  │    System         │
│             │           │  Integration      │
└─────────────┼───────────┼───────────────────┘
              │           │
    ┌─────────▼─────────┐ └─────────────────┐
    │       GUI         │                   │
    │  Components       │                   │
    └───────────────────┘                   │
              │                             │
    ┌─────────▼─────────┐         ┌─────────▼─────────┐
    │ Environment       │         │ System Tray       │
    │   Selector        │         │  Integration      │
    └───────────────────┘         └───────────────────┘
              │
    ┌─────────▼─────────┐
    │   Settings        │
    │    Dialog         │
    └───────────────────┘
```

## Core Components

### 1. Application Controller (`app_controller.py`)

**Purpose**: Central orchestrator for all application functionality

**Key Responsibilities**:
- Environment management (CRUD operations)
- System tray integration
- Application configuration management
- Signal coordination between components

**Key Methods**:
```python
setup_system_tray() -> bool           # Initialize system tray
launch_environment(env) -> bool       # Launch an environment
get_environments() -> List[Environment]  # Retrieve environments
add_environment(env) -> bool          # Add new environment
```

**Design Patterns**:
- **Observer Pattern**: Uses PyQt signals for component communication
- **Facade Pattern**: Provides simplified interface to complex subsystems
- **Singleton-like**: Single instance coordinates entire application

### 2. Data Models (`models.py`)

**Environment Model**:
```python
@dataclass
class Environment:
    name: str
    description: str = ""
    applications: List[Application] = field(default_factory=list)
    websites: List[Website] = field(default_factory=list)
    startup_delay: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

**Application Model**:
```python
@dataclass
class Application:
    name: str
    path: str
    arguments: str = ""
    working_directory: Optional[str] = None
    wait_for_exit: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

**Website Model**:
```python
@dataclass  
class Website:
    name: str
    url: str
    browser: Optional[str] = None
    new_tab: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

**Design Features**:
- **Immutable by Default**: Using dataclasses for type safety
- **UUID Identification**: Each entity has unique identifier
- **Serialization Support**: Built-in JSON conversion methods
- **Validation Methods**: Each model validates its own data

### 3. Storage System (`storage.py`)

**Purpose**: Manages persistent storage of environments and configuration

**Storage Format**: JSON files in Windows AppData directory
- **Configuration**: `%APPDATA%\EnvStarter\config.json`
- **Environments**: `%APPDATA%\EnvStarter\environments.json`

**Key Features**:
```python
class ConfigManager:
    def get_environments() -> List[Environment]
    def save_environments(environments: List[Environment])
    def add_environment(environment: Environment) -> bool
    def update_environment(environment: Environment) -> bool
    def delete_environment(environment_id: str) -> bool
```

**Error Handling**:
- Graceful handling of corrupted JSON files
- Automatic backup creation before modifications
- Recovery from missing configuration files

**Sample Configuration Structure**:
```json
{
  "version": "1.0.0",
  "first_run": false,
  "auto_start": true,
  "minimize_to_tray": true,
  "show_notifications": true,
  "last_selected_environment": "uuid-here",
  "window_position": {"x": 100, "y": 100},
  "window_size": {"width": 800, "height": 600}
}
```

### 4. Launch System (`launcher.py`)

**Purpose**: Handles environment launching with progress tracking

**Architecture**: Multi-threaded with worker threads for non-blocking launches

```python
class LaunchWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    item_launched = pyqtSignal(str, bool)
    launch_completed = pyqtSignal(bool)
```

**Launch Process**:
1. **Preparation**: Validate environment and items
2. **Startup Delay**: Wait if specified
3. **Sequential Launch**: Launch applications and websites in order
4. **Progress Updates**: Real-time status via signals
5. **Completion**: Report final status

**Application Launch Logic**:
```python
def _launch_application(self, app: Application) -> bool:
    # Expand environment variables
    app_path = os.path.expandvars(app.path)
    
    # Handle PATH lookup for simple commands
    if not Path(app_path).exists():
        # Search in Windows PATH
        
    # Prepare command with arguments
    cmd = [app_path] + app.arguments.split()
    
    # Launch with proper Windows flags
    process = subprocess.Popen(cmd, 
                              cwd=app.working_directory,
                              creationflags=subprocess.CREATE_NO_WINDOW)
```

**Website Launch Logic**:
```python  
def _launch_website(self, website: Website) -> bool:
    if website.browser:
        # Use specific browser
        subprocess.Popen([website.browser, website.url])
    else:
        # Use system default browser
        webbrowser.open(website.url, new=2 if website.new_tab else 1)
```

### 5. System Integration (`system_integration.py`)

**Purpose**: Windows-specific system integration features

**Windows Startup Integration**:
```python
def add_to_startup(self) -> bool:
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self.executable_path)
```

**Desktop Shortcut Creation**:
```python
def create_desktop_shortcut(self) -> bool:
    # Uses PowerShell COM objects to create proper Windows shortcuts
    ps_command = f'''
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
    $Shortcut.TargetPath = "{self.executable_path}"
    $Shortcut.Save()
    '''
```

**Installed Program Discovery**:
- Scans Windows registry uninstall entries
- Searches common installation directories  
- Provides program metadata (name, path, install location)

## GUI Architecture

### 1. Environment Selector (`environment_selector.py`)

**Design Pattern**: Model-View-Controller with PyQt6

**Layout Structure**:
```
┌─────────────────────────────────────────────┐
│                  Header                     │
├─────────────────┬───────────────────────────┤
│  Environment    │    Details & Progress     │
│     List        │                           │
│                 │                           │
│                 │                           │
├─────────────────┴───────────────────────────┤
│               Controls                      │
└─────────────────────────────────────────────┘
```

**Custom Widgets**:
- `EnvironmentListItem`: Rich list items with environment details
- `LaunchProgressWidget`: Progress tracking with logs

**Key Features**:
- Real-time launch progress updates
- Environment details preview
- Keyboard shortcuts support
- Responsive layout

### 2. Settings Dialog (`settings_dialog.py`)

**Architecture**: Tabbed interface with specialized forms

**Tab Structure**:
1. **General**: Application-wide settings
2. **Environments**: Environment CRUD operations  
3. **System**: Windows integration settings

**Custom Components**:
- `ApplicationEditWidget`: Form for application configuration
- `WebsiteEditWidget`: Form for website configuration
- `EnvironmentEditDialog`: Full environment editor

**Data Flow**:
```
Settings Dialog
    ↓ (user interactions)
App Controller  
    ↓ (data operations)
Storage Manager
    ↓ (persistence)
JSON Files
```

## Threading Model

### Main Thread
- **GUI Operations**: All PyQt6 widget interactions
- **Event Handling**: User interactions, system tray events
- **Signal Processing**: Inter-component communication

### Worker Threads  
- **Environment Launching**: `LaunchWorker` threads
- **System Operations**: File I/O, registry operations
- **Background Tasks**: Configuration loading/saving

### Thread Safety
- **Signal-Slot Communication**: All cross-thread communication via Qt signals
- **Immutable Data**: Environment/Application/Website models are effectively immutable
- **Atomic Operations**: Database-like operations for configuration changes

## Error Handling Strategy

### Layered Error Handling

**Level 1 - Model Validation**:
```python
def is_valid(self) -> bool:
    """Validate model data before operations"""
    # Check required fields, validate formats, etc.
```

**Level 2 - Operation Errors**:
```python
def add_environment(self, environment: Environment) -> bool:
    try:
        # Perform operation
        return True
    except Exception as e:
        logger.error(f"Failed to add environment: {e}")
        return False
```

**Level 3 - UI Error Display**:
```python
if not success:
    QMessageBox.warning(self, "Error", "Failed to save environment.")
```

### Error Categories

**Recoverable Errors**:
- Missing application files (warn user, allow editing)
- Invalid URLs (show validation message)
- Network connectivity issues (retry mechanism)

**Non-Recoverable Errors**:
- Corrupted configuration files (reset to defaults)
- Permission issues (show admin instructions)
- System API failures (graceful degradation)

## Security Considerations

### Input Validation

**Path Validation**:
```python
def validate_path(path: str) -> bool:
    # Prevent path traversal attacks
    # Validate executable extensions
    # Check file permissions
```

**URL Validation**:
```python
def validate_url(url: str) -> bool:
    # Ensure proper protocol (http/https)
    # Prevent local file access
    # Basic format validation
```

### Privilege Management

**Registry Operations**: Only modify HKEY_CURRENT_USER (no admin required)

**File System Access**: Limited to user's AppData directory

**Process Spawning**: Only launch user-configured applications

### Data Protection

**Local Storage Only**: No network data transmission

**User Consent**: All system modifications require user approval

**Reversible Operations**: All integrations can be cleanly removed

## Performance Characteristics

### Memory Usage
- **Base Application**: ~50MB RAM
- **Per Environment**: ~1KB storage
- **During Launch**: Minimal overhead (delegated to launched applications)

### CPU Usage  
- **Idle State**: Minimal (system tray only)
- **During Launch**: Brief spike for process creation
- **Steady State**: Near-zero background usage

### Storage Requirements
- **Application**: ~20MB installation
- **Configuration**: <1MB for typical usage
- **Logs**: Configurable retention (default 30 days)

### Startup Performance
- **Cold Start**: <2 seconds to system tray
- **Environment Launch**: Depends on configured applications
- **UI Response**: <100ms for all interactions

## Extensibility Points

### Plugin Architecture (Future)
```python
class EnvironmentPlugin:
    def pre_launch(self, environment: Environment) -> bool:
        """Called before environment launch"""
        
    def post_launch(self, environment: Environment, success: bool):
        """Called after environment launch"""
```

### Custom Launchers
```python
class CustomLauncher:
    def can_handle(self, item: Union[Application, Website]) -> bool:
        """Check if this launcher can handle the item"""
        
    def launch(self, item: Union[Application, Website]) -> bool:
        """Launch the item using custom logic"""
```

### Configuration Providers
```python
class ConfigProvider:
    def load_environments(self) -> List[Environment]:
        """Load environments from custom source"""
        
    def save_environments(self, environments: List[Environment]):
        """Save environments to custom storage"""
```

## Testing Strategy

### Unit Tests
- **Model Validation**: Test all data model validation logic
- **Storage Operations**: Test JSON serialization/deserialization
- **Launcher Logic**: Mock process creation for testing

### Integration Tests  
- **GUI Workflows**: Test complete user workflows
- **System Integration**: Test Windows registry/shortcut operations
- **Error Scenarios**: Test error handling and recovery

### Performance Tests
- **Large Environments**: Test with 50+ applications/websites
- **Memory Leaks**: Long-running stability tests
- **Concurrent Operations**: Multiple simultaneous launches

### Compatibility Tests
- **Windows Versions**: Test on Windows 10/11
- **Python Versions**: Test Python 3.8-3.11
- **PyQt6 Versions**: Test different PyQt6 releases

## Deployment Considerations

### Distribution Options

**Source Distribution**:
- Git repository with setup.py
- Requires Python installation
- Best for developers

**Binary Distribution** (Future):
- PyInstaller-generated executable
- Self-contained Windows installer
- Best for end users

### System Requirements

**Minimum Python Version**: 3.8 (for typing support)

**Required Packages**:
- PyQt6 >= 6.6.0 (GUI framework)
- pystray >= 0.19.4 (system tray)
- Pillow >= 10.0.0 (image processing)
- psutil >= 5.9.0 (process management)

**Windows Dependencies**:
- winreg (built-in, registry access)
- webbrowser (built-in, URL opening)
- subprocess (built-in, process launching)

### Installation Verification

**Health Check**:
```python
def verify_installation():
    # Check Python version
    # Verify all dependencies
    # Test system tray availability  
    # Validate Windows integration
    # Create test configuration
```

This technical specification ensures EnvStarter is built with proper architecture, error handling, security, and extensibility considerations while meeting all the original requirements.