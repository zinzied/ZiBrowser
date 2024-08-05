### ZiBrowser-
## Fast and Stable and not eats Rams xD

   ![image](https://github.com/user-attachments/assets/49e67c4b-28aa-4158-ace8-0a98492c5e3d)

### Project Description: ZiBrowser

**ZiBrowser** is a custom web browser built using PyQt5 and the Qt WebEngine framework. It provides a user-friendly interface with essential browsing features, including tabbed browsing, navigation controls, download management, history management, and settings configuration. The browser is designed to be lightweight yet functional, offering a familiar browsing experience with additional customization options.

#### Key Features:

1. **Tabbed Browsing**:
   - Users can open multiple tabs and switch between them easily.
   - Double-clicking on the tab bar opens a new tab.
   - Tabs can be closed individually, and the browser ensures at least one tab remains open.

2. **Navigation Controls**:
   - Back, Forward, Reload, and Home buttons for easy navigation.
   - A URL bar for entering and navigating to specific web addresses.
   - A New Tab button to quickly open a new tab.

3. **Download Management**:
   - Handles file downloads with a user prompt to choose the save location.
   - Displays ongoing and completed downloads in a dedicated downloads window.
   - Shows download progress and updates the status upon completion.

4. **History Management**:
   - Keeps track of browsing history.
   - Provides a history window to view and revisit previously visited sites.
   - Option to clear browsing history.

5. **Settings Configuration**:
   - Allows users to delete all cookies.
   - Provides proxy settings configuration to set up an HTTP proxy.
   - Settings are accessible through a settings menu in the navigation bar.

6. **Persistent Cookies**:
   - Stores cookies persistently to maintain session data across browser restarts.
   - Cookies are stored in a user-specific directory.

#### Technical Details:

- **PyQt5**: The browser is built using PyQt5, a set of Python bindings for the Qt application framework.
- **Qt WebEngine**: Utilizes the Qt WebEngine module to render web pages and handle web content.
- **QWebEngineProfile**: Manages persistent cookies and storage.
- **QWebEngineView**: Provides the main widget for displaying web content.
- **QNetworkProxy**: Allows configuration of network proxy settings.

#### Code Structure:

- **Browser Class**: The main class that sets up the browser window, navigation bar, tabs, and other UI elements.
- **add_new_tab Method**: Adds a new tab with a web view and connects necessary signals.
- **handle_download Method**: Manages file downloads, prompts the user for a save location, and updates the download list.
- **update_download_progress Method**: Updates the download progress in the downloads list.
- **download_finished Method**: Updates the status of completed downloads.
- **show_history Method**: Displays the browsing history in a dialog.
- **show_settings Method**: Opens the settings dialog for cookie and proxy management.
- **show_proxy_settings Method**: Opens the proxy settings dialog.
- **set_proxy Method**: Configures the network proxy settings.
- **show_downloads Method**: Displays the downloads list.
- **delete_history Method**: Clears the browsing history.
- **delete_all_cookies Method**: Deletes all stored cookies.

#### Usage:

To run the browser, execute the script using Python. Ensure that PyQt5 and other dependencies are installed. The browser window will open, allowing users to navigate the web, manage downloads, view history, and configure settings.

```bash
pip install -r requirements.txt
```
```bash
python zibrowser.py
```

ZiBrowser aims to provide a simple yet effective browsing experience with essential features and customization options, making it a versatile tool for everyday web browsing.
