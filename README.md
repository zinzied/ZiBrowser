### ZiBrowser
## Fast and Stable and Memory-Efficient Browser

![image](https://github.com/user-attachments/assets/49e67c4b-28aa-4158-ace8-0a98492c5e3d)

### Project Description: ZiBrowser

**ZiBrowser** is a custom web browser built using PyQt5 and the Qt WebEngine framework. It provides a user-friendly interface with essential browsing features, including tabbed browsing, navigation controls, download management, history management, and settings configuration. The browser is designed to be lightweight and memory-efficient, offering a familiar browsing experience with advanced customization options.

#### Key Features:

1. **Performance Optimization**:
   - Memory management system with automatic tab suspension
   - Performance profiles (Balanced, Performance, Minimal)
   - Resource monitor for tracking memory and CPU usage
   - Cache control system for optimal performance
   - Memory-saving modes for reduced resource usage

2. **Search Engine Management**:
   - Multiple built-in search engines (Google, Bing, DuckDuckGo, Yahoo, Ecosia)
   - Customizable search engine settings
   - Ability to add custom search engines
   - Quick search engine switching from the navigation bar
   - Default search engine configuration

3. **Tabbed Browsing**:
   - Intelligent tab management with automatic suspension
   - Double-clicking on the tab bar opens a new tab
   - Tabs default to Google search for convenience
   - Tab suspension for inactive tabs to save memory
   - Tabs can be closed individually

4. **Navigation Controls**:
   - Back, Forward, Reload, and Home buttons
   - Smart URL bar with search integration
   - Quick access to favorite search engines
   - New Tab button with customizable default page

5. **Download Management**:
   - File download handling with save location prompt
   - Download progress tracking
   - Dedicated downloads window
   - Status updates for completed downloads

6. **Memory Management**:
   - Memory manager tool for cache control
   - Performance mode toggle
   - Image loading controls
   - Automatic tab suspension after inactivity
   - Resource usage monitoring

7. **Settings Configuration**:
   - Cookie management
   - Proxy settings
   - Search engine configuration
   - Performance profile selection
   - Memory optimization settings

#### Technical Improvements:

- **Memory Optimization**: Implemented smart memory management with tab suspension
- **Performance Profiles**: Added configurable performance modes
- **Resource Monitor**: Real-time tracking of browser resource usage
- **Search Engine Framework**: Flexible search engine management system
- **Cache Control**: Intelligent cache management for better performance

#### Code Structure:

- **Browser Class**: Main browser implementation with memory management
- **AdBlocker Class**: Handles ad blocking functionality
- **Performance Profiles**: Manages different performance settings
- **Search Engine Manager**: Handles search engine configuration
- **Memory Manager**: Controls browser memory usage
- **Tab Suspender**: Manages inactive tab suspension

#### Usage:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the browser:
```bash
python zibrowser.py
```

3. Performance Tips:
   - Use Performance Mode for lower memory usage
   - Enable tab suspension for longer browsing sessions
   - Monitor resource usage through the Memory Manager
   - Configure custom search engines for efficient searching

ZiBrowser now offers enhanced performance features while maintaining a simple and effective browsing experience. The focus on memory efficiency and customization makes it ideal for users who want a lightweight yet capable web browser.

#### New Settings:

- Memory Manager: Access through Settings → Memory Manager
- Search Engines: Configure in Settings → Search Engine Settings
- Performance Profiles: Available in Settings → Performance
- Resource Monitor: Check system usage in Settings → Resource Monitor
