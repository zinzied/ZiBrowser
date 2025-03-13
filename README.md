# ZiBrowser
## A Fast, Stable, and Memory-Efficient Web Browser

![ZiBrowser Logo](https://github.com/user-attachments/assets/49e67c4b-28aa-4158-ace8-0a98492c5e3d)

## Project Description

**ZiBrowser** is a modern web browser built with PyQt5 and Qt WebEngine, focusing on performance and user experience. It combines essential browsing features with advanced memory management and customization options.

## Key Features

### 1. Performance Optimization
- **Smart Memory Management**
  - Automatic tab suspension for inactive tabs
  - Configurable performance profiles (Balanced/Performance/Minimal)
  - Real-time resource monitoring
  - Intelligent cache management
  - Memory-saving modes

### 2. Search Engine Integration
- **Multiple Search Engines**
  - Google, Bing, DuckDuckGo, Yahoo, Ecosia
  - Custom search engine support
  - Quick engine switching from navbar
  - Per-tab search engine selection
  - Default engine configuration

### 3. Advanced Browsing Features
- **Tab Management**
  - Intelligent tab suspension
  - Session restoration
  - Tab pinning support
  - Background tab loading
  - Tab grouping

### 4. Media Handling
- **Enhanced Video Support**
  - HTML5 video optimization
  - Full-screen support
  - Picture-in-Picture mode
  - Media controls integration
  - Download capability

### 5. Security Features
- **Privacy Protection**
  - Built-in ad blocker
  - Cookie management
  - Private browsing mode
  - Proxy support
  - Site permissions control

## Technical Details

### System Requirements
- Python 3.6+
- PyQt5
- QtWebEngine
- Windows/Linux/macOS support

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/zibrowser.git
cd zibrowser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the browser:
```bash
python zibrowser.py
```

### Performance Tips
1. **Memory Optimization**
   - Enable tab suspension in Settings
   - Use Performance mode for resource-intensive sites
   - Clear cache regularly via Memory Manager

2. **Speed Improvements**
   - Configure custom search engines
   - Enable hardware acceleration
   - Use the built-in ad blocker

## Component Architecture

### Core Components
- `Browser`: Main application controller
- `AdBlocker`: Advertisement filtering
- `MemoryManager`: Resource optimization
- `SearchEngine`: Search integration
- `TabManager`: Tab handling and suspension

### Key Features Implementation
```python
ZiBrowser/
├── core/
│   ├── browser.py      # Main browser implementation
│   ├── adblocker.py    # Ad blocking functionality
│   └── memory.py       # Memory management
├── ui/
│   ├── mainwindow.py   # User interface
│   └── controls.py     # Browser controls
└── utils/
    ├── settings.py     # Configuration management
    └── profiles.py     # Performance profiles
```

## Latest Updates

### Version 1.0
- Implemented smart memory management
- Added multiple search engine support
- Integrated ad blocking system
- Enhanced download manager
- Added performance profiles

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- Author: Zied Boughdir
- GitHub: [github.com/zinzied](https://github.com/zinzied)
- Issues: [github.com/zinzied/zibrowser/issues](https://github.com/zinzied/zibrowser/issues)
