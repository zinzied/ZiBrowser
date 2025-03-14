import sys
from PyQt5.QtCore import *
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebChannel import QWebChannel  # Add this import
import os
import logging

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.ad_domains = [
            "ads.", "doubleclick.", "advertising.", "banners.",
            "analytics.", "trackers.", "pixel."
        ]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if any(ad in url.lower() for ad in self.ad_domains):
            info.block(True)

class BrowserLogger:
    def __init__(self):
        self.logger = logging.getLogger('ZiBrowser')
        self.logger.setLevel(logging.WARNING)
        
        handler = logging.FileHandler('zibrowser.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def log_js_error(self, message):
        self.logger.warning(f"JavaScript Error: {message}")
    
    def log_video_error(self, message):
        self.logger.warning(f"Video Error: {message}")

# Add this after your class definitions but before Browser class
DEFAULT_SEARCH_ENGINES = {
    'Google': 'https://www.google.com/search?q={}',
    'Bing': 'https://www.bing.com/search?q={}',
    'DuckDuckGo': 'https://duckduckgo.com/?q={}',
    'Yahoo': 'https://search.yahoo.com/search?p={}',
    'Ecosia': 'https://www.ecosia.org/search?q={}'
}

# Add this class to handle JavaScript-Python bridge
class JavaScriptBridge(QObject):
    def __init__(self):
        super().__init__()
        self.logger = BrowserLogger()

    @pyqtSlot(str)
    def log(self, message):
        """Log messages from JavaScript"""
        print(f"JavaScript: {message}")
        self.logger.log_js_error(message)

    @pyqtSlot(str, result=str)
    def processPythonData(self, data):
        """Process data from JavaScript"""
        try:
            return f"Processed by Python: {data.upper()}"
        except Exception as e:
            self.log(f"Error processing data: {e}")
            return str(e)

    @pyqtSlot(str)
    def saveToFile(self, content):
        """Save data from JavaScript"""
        try:
            with open('browser_data.txt', 'a', encoding='utf-8') as f:
                f.write(f"{content}\n")
        except Exception as e:
            self.log(f"Error saving data: {e}")

    @pyqtSlot(str)
    def onVideoDownloaded(self, url):
        QMessageBox.information(None, "Success", f"Video downloaded: {url}")

    @pyqtSlot(str)
    def onVideoError(self, error):
        QMessageBox.warning(None, "Error", f"Video error: {error}")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create toolbar before other UI elements
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Set up the profile for storing cookies
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        cookies_path = os.path.join(os.path.expanduser("~"), "ZiBrowserCookies")
        if not os.path.exists(cookies_path):
            os.makedirs(cookies_path)
        self.profile.setPersistentStoragePath(cookies_path)

        # Memory management settings
        self.profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100MB cache limit
        self.profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.profile.clearHttpCache()

        # Configure web settings
        self.settings = QWebEngineSettings.defaultSettings()
        self.settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        self.settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.ShowScrollBars, True)
        self.settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)  # Disable by default
        self.settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        
        # Set modern user agent
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)
        self.showMaximized()

        # Set window icon
        self.setWindowIcon(QIcon('images/icon.png'))

        # Navigation bar
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction(QIcon('images/back.png'), 'Back', self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navbar.addAction(back_btn)

        forward_btn = QAction(QIcon('images/forward.png'), 'Forward', self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navbar.addAction(forward_btn)

        reload_btn = QAction(QIcon('images/reload.png'), 'Reload', self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navbar.addAction(reload_btn)

        home_btn = QAction(QIcon('images/home.png'), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        new_tab_btn = QAction(QIcon('images/newtab.png'), 'New Tab', self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab_btn)

        history_btn = QAction(QIcon('images/history.png'), 'History', self)
        history_btn.triggered.connect(self.show_history)
        navbar.addAction(history_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Settings menu
        settings_btn = QToolButton()
        settings_btn.setIcon(QIcon('images/setting.png'))
        settings_btn.setPopupMode(QToolButton.InstantPopup)
        settings_menu = QMenu()

        settings_action = QAction(QIcon('images/settings.png'), 'Settings', self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)

        downloads_action = QAction(QIcon('images/downloads.png'), 'Downloads', self)
        downloads_action.triggered.connect(self.show_downloads)
        settings_menu.addAction(downloads_action)

        delete_history_action = QAction(QIcon('images/delete.png'), 'Delete History', self)
        delete_history_action.triggered.connect(self.delete_history)
        settings_menu.addAction(delete_history_action)

        about_action = QAction(QIcon('images/about.png'), 'About', self)
        about_action.triggered.connect(self.show_about)
        settings_menu.addAction(about_action)

        private_window_action = QAction(QIcon('images/private.png'), 'New Private Window', self)
        private_window_action.triggered.connect(self.open_private_window)
        settings_menu.addAction(private_window_action)

        bookmark_action = QAction(QIcon('images/bookmark.png'), 'Add Bookmark', self)
        bookmark_action.triggered.connect(self.add_bookmark)
        settings_menu.addAction(bookmark_action)

        show_bookmarks_action = QAction(QIcon('images/bookmarks.png'), 'Show Bookmarks', self)
        show_bookmarks_action.triggered.connect(self.show_bookmarks)
        settings_menu.addAction(show_bookmarks_action)

        dark_mode_action = QAction(QIcon('images/dark-mode.png'), 'Toggle Dark Mode', self)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        settings_menu.addAction(dark_mode_action)

        memory_manager_action = QAction(QIcon('images/memory.png'), 'Memory Manager', self)
        memory_manager_action.triggered.connect(self.show_memory_manager)
        settings_menu.addAction(memory_manager_action)

        search_engine_settings_action = QAction(QIcon('images/search.png'), 'Search Engine Settings', self)
        search_engine_settings_action.triggered.connect(self.show_search_engine_settings)
        settings_menu.addAction(search_engine_settings_action)

        test_bridge_action = QAction(QIcon('images/test.png'), 'Test JS Bridge', self)
        test_bridge_action.triggered.connect(self.test_python_js_bridge)
        settings_menu.addAction(test_bridge_action)

        settings_btn.setMenu(settings_menu)
        navbar.addWidget(settings_btn)

        # Load search engine settings
        self.settings = QSettings('ZiBrowser', 'Settings')
        self.current_search_engine = self.settings.value('search_engine', 'Google')
        self.search_engines = self.settings.value('search_engines', DEFAULT_SEARCH_ENGINES)
        
        # Add search engine selector to navbar
        self.search_engine_selector = QComboBox()
        self.search_engine_selector.addItems(self.search_engines.keys())
        self.search_engine_selector.setCurrentText(self.current_search_engine)
        self.search_engine_selector.currentTextChanged.connect(self.change_search_engine)
        navbar.addWidget(self.search_engine_selector)

        self.add_new_tab(self.get_search_engine_url(), self.current_search_engine)

        # Download manager
        self.downloads_list = QListWidget()
        self.downloads_list.setWindowTitle("Downloads")
        self.downloads_list.setFixedSize(400, 300)

        # Setup tab suspender
        self.setup_tab_suspender()

        # Setup performance profiles
        self.setup_performance_profiles()

        # Configure error handling for WebEngine
        self.page_error_handler = QWebEnginePage(self)
        self.page_error_handler.javaScriptConsoleMessage = self.handle_js_console

        # Add video controls
        self.add_video_controls()

        # Add video storage support
        self.setup_video_storage(self.tabs.currentWidget())
        self.add_video_controls()
        
        # Create videos directory
        self.tabs.currentWidget().page().runJavaScript("""
            videoHandler.store.getDir('videos', { create: true }, () => {
                console.log('Videos directory created');
            });
        """)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None or not isinstance(qurl, QUrl):
            qurl = self.get_search_engine_url()
        
        browser = QWebEngineView()
        
        # Configure page settings for video
        page = QWebEnginePage(self.profile, browser)
        browser.setPage(page)
        
        # Enable video fullscreen
        page.fullScreenRequested.connect(lambda request: request.accept())
        
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

        # Connect the downloadRequested signal
        browser.page().profile().downloadRequested.connect(self.handle_download)

        # Inject compatibility polyfills
        self.inject_compatibility_polyfills(browser)
        
        # Inject JavaScript polyfill for replaceAll
        browser.page().runJavaScript("""
            if (!String.prototype.replaceAll) {
                String.prototype.replaceAll = function(search, replacement) {
                    try {
                        return this.split(search).join(replacement);
                    } catch (e) {
                        console.warn('replaceAll error:', e);
                        return this;
                    }
                };
            }
        """)

        # Create and set the ad blocker
        ad_blocker = AdBlocker()
        browser.page().profile().setUrlRequestInterceptor(ad_blocker)

        # Inject video compatibility fixes
        self.inject_video_compatibility_fixes(browser)

        # Configure video settings
        self.configure_video_settings(browser)

        # Inject media error handler
        self.inject_media_error_handler(browser)
        
        # Enable IndexedDB with fallback
        self.enable_indexed_db(browser)

        # Initialize QWebChannel properly
        channel = QWebChannel(browser.page())
        browser.page().setWebChannel(channel)
        
        # Add JavaScript bridge
        self.js_bridge = JavaScriptBridge()
        channel.registerObject('python', self.js_bridge)
        
        # Inject required QWebChannel.js first
        browser.page().runJavaScript("""
            if (!window.qt) {
                window.qt = { webChannelTransport: null };
            }
            
            window.onload = function() {
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.python = channel.objects.python;
                    
                    // Define global functions after bridge is established
                    window.logToPython = function(message) {
                        python.log(message);
                    };
                    
                    window.processPythonData = function(data) {
                        return python.processPythonData(data);
                    };
                    
                    window.saveToPython = function(content) {
                        python.saveToFile(content);
                    };
                    
                    // Signal that bridge is ready
                    console.log('Python bridge initialized');
                });
            };
        """)

        # Inject interaction examples
        self.inject_interaction_examples(browser)

        # Inject error handlers
        self.inject_error_handlers(browser)

        # Setup video storage
        self.setup_video_storage(browser)

        # Inject video handler
        self.inject_video_handler(browser)

        return browser

    def handle_download(self, download):
        # Ask the user where to save the file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path(), options=options)
        if file_path:
            download.setPath(file_path)
            download.accept()

            # Add download item to the downloads list
            item = QListWidgetItem(f"Downloading {os.path.basename(file_path)}")
            self.downloads_list.addItem(item)

            # Connect signals to update the download item
            download.downloadProgress.connect(lambda received, total, item=item: self.update_download_progress(received, total, item))
            download.finished.connect(lambda item=item: self.download_finished(item))

    def update_download_progress(self, received, total, item):
        if total > 0:
            progress = int(received / total * 100)
            item.setText(f"Downloading {item.text().split(' ')[1]} - {progress}%")

    def download_finished(self, item):
        item.setText(f"Downloaded {item.text().split(' ')[1]}")

    def tab_open_doubleclick(self, i):
        if i == -1:
            # Open Google in new tab when double-clicking
            self.add_new_tab(QUrl('https://www.google.com'), 'Google')

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_url(qurl)
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def navigate_home(self):
        # Update home button to use https
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        
        # Check if the input is a URL or search term
        if not url.startswith(('http://', 'https://', 'file://')):
            # Check if it's a domain name
            if '.' in url and ' ' not in url:
                url = 'http://' + url
            else:
                # It's a search term
                search_template = self.search_engines[self.current_search_engine]
                url = search_template.format(QUrl.toPercentEncoding(url).data().decode())
        
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return

        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - ZiBrowser")

    def show_history(self):
        history = self.tabs.currentWidget().history()
        history_list = history.items()
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("History")
        history_dialog.setFixedSize(800, 600)  # Set the size of the history dialog

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for item in history_list:
            btn = QPushButton(item.url().toString())
            btn.clicked.connect(lambda checked, url=item.url(): self.tabs.currentWidget().setUrl(url))
            scroll_layout.addWidget(btn)

        scroll_area.setWidget(scroll_content)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        history_dialog.setLayout(layout)
        history_dialog.exec_()

    def show_settings(self):
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        settings_dialog.setFixedSize(400, 300)

        layout = QVBoxLayout()

        delete_cookies_btn = QPushButton("Delete All Cookies")
        delete_cookies_btn.clicked.connect(self.delete_all_cookies)
        layout.addWidget(delete_cookies_btn)

        proxy_settings_btn = QPushButton("Proxy Settings")
        proxy_settings_btn.clicked.connect(self.show_proxy_settings)
        layout.addWidget(proxy_settings_btn)

        memory_manager_btn = QPushButton("Memory Manager")
        memory_manager_btn.clicked.connect(self.show_memory_manager)
        layout.addWidget(memory_manager_btn)

        settings_dialog.setLayout(layout)
        settings_dialog.exec_()

    def show_proxy_settings(self):
        proxy_dialog = QDialog(self)
        proxy_dialog.setWindowTitle("Proxy Settings")
        proxy_dialog.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.proxy_address = QLineEdit()
        self.proxy_address.setPlaceholderText("Proxy Address")
        layout.addWidget(self.proxy_address)

        self.proxy_port = QLineEdit()
        self.proxy_port.setPlaceholderText("Proxy Port")
        layout.addWidget(self.proxy_port)

        set_proxy_btn = QPushButton("Set Proxy")
        set_proxy_btn.clicked.connect(self.set_proxy)
        layout.addWidget(set_proxy_btn)

        proxy_dialog.setLayout(layout)
        proxy_dialog.exec_()

    def set_proxy(self):
        proxy_address = self.proxy_address.text()
        proxy_port = self.proxy_port.text()

        if proxy_address and proxy_port:
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.HttpProxy)
            proxy.setHostName(proxy_address)
            proxy.setPort(int(proxy_port))
            QNetworkProxy.setApplicationProxy(proxy)
            QMessageBox.information(self, "Proxy Set", f"Proxy set to {proxy_address}:{proxy_port}")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter both proxy address and port")

    def show_downloads(self):
        self.downloads_list.show()

    def delete_history(self):
        self.tabs.currentWidget().history().clear()

    def delete_all_cookies(self):
        self.profile.cookieStore().deleteAllCookies()

    def show_about(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About ZiBrowser")
        about_dialog.setFixedSize(300, 200)

        layout = QVBoxLayout()

        label = QLabel("ZiBrowser\nCreated by Zied Boughdir 2024")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        github_link = QLabel('<a href="https://www.github.com/zinzied">GitHub Profile</a>')
        github_link.setAlignment(Qt.AlignCenter)
        github_link.setOpenExternalLinks(True)
        layout.addWidget(github_link)

        about_dialog.setLayout(layout)
        about_dialog.exec_()

    def add_bookmark(self):
        current_url = self.tabs.currentWidget().url().toString()
        current_title = self.tabs.currentWidget().page().title()
        
        settings = QSettings('ZiBrowser', 'Bookmarks')
        bookmarks = settings.value('bookmarks', {})
        bookmarks[current_title] = current_url
        settings.setValue('bookmarks', bookmarks)
        
        QMessageBox.information(self, "Bookmark Added", f"'{current_title}' has been bookmarked!")

    def show_bookmarks(self):
        settings = QSettings('ZiBrowser', 'Bookmarks')
        bookmarks = settings.value('bookmarks', {})
        
        bookmark_dialog = QDialog(self)
        bookmark_dialog.setWindowTitle("Bookmarks")
        bookmark_dialog.setFixedSize(600, 400)
        
        layout = QVBoxLayout()
        for title, url in bookmarks.items():
            bookmark_btn = QPushButton(f"{title}\n{url}")
            bookmark_btn.clicked.connect(lambda _, u=url: self.tabs.currentWidget().setUrl(QUrl(u)))
            layout.addWidget(bookmark_btn)
        
        bookmark_dialog.setLayout(layout)
        bookmark_dialog.exec_()

    def toggle_dark_mode(self):
        dark_css = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QLineEdit {
            background-color: #3b3b3b;
            border: 1px solid #555555;
            color: #ffffff;
        }
        QToolBar {
            background-color: #333333;
            border: none;
        }
        """
        
        if not hasattr(self, 'dark_mode_enabled'):
            self.dark_mode_enabled = False
        
        self.dark_mode_enabled = not self.dark_mode_enabled
        if self.dark_mode_enabled:
            self.setStyleSheet(dark_css)
        else:
            self.setStyleSheet("")

    def pin_tab(self, index):
        if not hasattr(self.tabs, 'pinned_tabs'):
            self.tabs.pinned_tabs = set()
        
        if index in self.tabs.pinned_tabs:
            self.tabs.pinned_tabs.remove(index)
            self.tabs.setTabIcon(index, QIcon())
        else:
            self.tabs.pinned_tabs.add(index)
            self.tabs.setTabIcon(index, QIcon('images/pin.png'))
            self.tabs.tabBar().moveTab(index, 0)

    def open_private_window(self):
        # Create a new private profile
        private_profile = QWebEngineProfile(None)  # Pass None to create a non-persistent profile
        
        # Create new browser window
        private_window = Browser()
        private_window.setWindowTitle("ZiBrowser (Private Mode)")
        
        # Set up the private profile
        private_window.profile = private_profile
        private_window.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        private_window.profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        private_window.profile.setHttpUserAgent(self.profile.httpUserAgent())
        
        # Set a different color scheme for private windows
        private_window.setStyleSheet("""
            QMainWindow { 
                background-color: #2b0b3f; 
            }
            QToolBar {
                background-color: #3b1b4f;
            }
            QTabWidget::pane {
                border-top: 2px solid #4b2b5f;
            }
            QTabBar::tab {
                background-color: #3b1b4f;
                color: white;
            }
            QTabBar::tab:selected {
                background-color: #4b2b5f;
            }
        """)
        
        # Show the private window
        private_window.show()
        
        # Clear data when window is closed
        private_window.destroyed.connect(lambda: self.cleanup_private_profile(private_profile))

    def cleanup_private_profile(self, profile):
        """Clean up the private profile when window is closed"""
        profile.clearAllVisitedLinks()
        profile.clearHttpCache()
        profile.cookieStore().deleteAllCookies()

    def handle_fullscreen(self, request):
        request.accept()
        if request.toggleOn():
            self.tabs.currentWidget().setParent(None)
            self.tabs.currentWidget().showFullScreen()
        else:
            self.tabs.currentWidget().setParent(self.tabs)
            self.tabs.currentWidget().showNormal()

    def show_memory_manager(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Memory Manager")
        dialog.setFixedSize(400, 300)
        layout = QVBoxLayout()

        # Memory info
        mem_info = QLabel("Memory Management Tools")
        layout.addWidget(mem_info)

        # Clear memory button
        clear_mem_btn = QPushButton("Clear Memory Cache")
        clear_mem_btn.clicked.connect(self.clear_memory)
        layout.addWidget(clear_mem_btn)

        # Performance mode toggle
        perf_mode = QCheckBox("Performance Mode (Reduces Memory Usage)")
        perf_mode.setChecked(not self.settings.testAttribute(QWebEngineSettings.WebGLEnabled))
        perf_mode.stateChanged.connect(self.toggle_performance_mode)
        layout.addWidget(perf_mode)

        # Image loading toggle
        img_load = QCheckBox("Load Images (Disable to save memory)")
        img_load.setChecked(self.settings.testAttribute(QWebEngineSettings.AutoLoadImages))
        img_load.stateChanged.connect(self.toggle_image_loading)
        layout.addWidget(img_load)

        dialog.setLayout(layout)
        dialog.exec_()

    def clear_memory(self):
        self.profile.clearHttpCache()
        self.profile.clearAllVisitedLinks()
        self.profile.cookieStore().deleteAllCookies()
        QWebEngineProfile.defaultProfile().clearAllVisitedLinks()
        
        for i in range(self.tabs.count()):
            self.tabs.widget(i).page().profile().clearHttpCache()
        
        QMessageBox.information(self, "Memory Cleared", "Browser memory has been cleared!")

    def toggle_performance_mode(self, state):
        self.settings.setAttribute(QWebEngineSettings.WebGLEnabled, not state)
        self.settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, not state)
        self.settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, not state)
        
        for i in range(self.tabs.count()):
            self.tabs.widget(i).reload()

    def toggle_image_loading(self, state):
        self.settings.setAttribute(QWebEngineSettings.AutoLoadImages, state)
        for i in range(self.tabs.count()):
            self.tabs.widget(i).reload()

    def setup_tab_suspender(self):
        self.suspend_timer = QTimer(self)
        self.suspend_timer.timeout.connect(self.check_inactive_tabs)
        self.suspend_timer.start(60000)  # Check every minute
        self.tab_last_used = {}

    def check_inactive_tabs(self):
        current_tab = self.tabs.currentWidget()
        current_time = QDateTime.currentDateTime()
        
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab != current_tab:
                if tab not in self.tab_last_used:
                    self.tab_last_used[tab] = current_time
                elif self.tab_last_used[tab].secsTo(current_time) > 1800:  # 30 minutes
                    self.suspend_tab(tab, i)

    def suspend_tab(self, tab, index):
        if not hasattr(tab, 'suspended'):
            url = tab.url()
            tab.suspended = True
            tab.suspended_url = url
            blank_page = QUrl('about:blank')
            tab.setUrl(blank_page)
            self.tabs.setTabIcon(index, QIcon('images/suspended.png'))
            self.tabs.setTabText(index, "[Suspended] " + self.tabs.tabText(index))

    def resume_tab(self, tab, index):
        if hasattr(tab, 'suspended') and tab.suspended:
            tab.setUrl(tab.suspended_url)
            tab.suspended = False
            del tab.suspended_url
            self.tabs.setTabIcon(index, QIcon())
            text = self.tabs.tabText(index)
            self.tabs.setTabText(index, text.replace("[Suspended] ", ""))

    def show_resource_monitor(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Resource Monitor")
        dialog.setFixedSize(400, 200)
        layout = QVBoxLayout()

        # Memory usage info
        import psutil
        process = psutil.Process()
        mem_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()

        info_label = QLabel(f"""
        Memory Usage: {mem_usage:.1f} MB
        CPU Usage: {cpu_usage}%
        Active Tabs: {self.tabs.count()}
        Cache Size: {self.profile.httpCacheMaximumSize() / 1024 / 1024:.1f} MB
        """)
        layout.addWidget(info_label)

        dialog.setLayout(layout)
        dialog.exec_()

    def setup_performance_profiles(self):
        self.performance_profiles = {
            'balanced': {
                'webgl': True,
                'javascript': True,
                'images': True,
                'animations': True
            },
            'performance': {
                'webgl': False,
                'javascript': True,
                'images': True,
                'animations': False
            },
            'minimal': {
                'webgl': False,
                'javascript': False,
                'images': False,
                'animations': False
            }
        }

    def apply_performance_profile(self, profile_name):
        if profile_name in self.performance_profiles:
            profile = self.performance_profiles[profile_name]
            self.settings.setAttribute(QWebEngineSettings.WebGLEnabled, profile['webgl'])
            self.settings.setAttribute(QWebEngineSettings.JavascriptEnabled, profile['javascript'])
            self.settings.setAttribute(QWebEngineSettings.AutoLoadImages, profile['images'])
            self.settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, profile['animations'])
            
            for i in range(self.tabs.count()):
                self.tabs.widget(i).reload()

    def change_search_engine(self, engine_name):
        self.current_search_engine = engine_name
        self.settings.setValue('search_engine', engine_name)

    def show_search_engine_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Engine Settings")
        dialog.setFixedSize(400, 300)
        layout = QVBoxLayout()

        # Default search engine selector
        default_label = QLabel("Default Search Engine:")
        layout.addWidget(default_label)
        
        engine_selector = QComboBox()
        engine_selector.addItems(self.search_engines.keys())
        engine_selector.setCurrentText(self.current_search_engine)
        engine_selector.currentTextChanged.connect(self.change_search_engine)
        layout.addWidget(engine_selector)

        # Add custom search engine
        add_label = QLabel("Add Custom Search Engine:")
        layout.addWidget(add_label)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Search Engine Name")
        layout.addWidget(name_input)
        
        url_input = QLineEdit()
        url_input.setPlaceholderText("URL Template (use {} for search term)")
        layout.addWidget(url_input)
        
        add_btn = QPushButton("Add Search Engine")
        add_btn.clicked.connect(lambda: self.add_search_engine(name_input.text(), url_input.text()))
        layout.addWidget(add_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_search_engine(self, name, url_template):
        if name and url_template and '{}' in url_template:
            self.search_engines[name] = url_template
            self.settings.setValue('search_engines', self.search_engines)
            self.search_engine_selector.addItem(name)
            QMessageBox.information(self, "Success", f"Added search engine: {name}")
        else:
            QMessageBox.warning(self, "Error", "Please enter valid name and URL template")

    def inject_compatibility_polyfills(self, browser):
        polyfills = """
        // Polyfill for replaceChildren
        if (!Element.prototype.replaceChildren) {
            Element.prototype.replaceChildren = function(...nodes) {
                while (this.lastChild) {
                    this.removeChild(this.lastChild);
                }
                if (nodes.length) {
                    this.append(...nodes);
                }
            };
        }

        // Polyfill for modern array methods
        if (!Array.prototype.at) {
            Array.prototype.at = function(index) {
                return index >= 0 ? this[index] : this[this.length + index];
            };
        }

        // Error handling for Promise rejections
        window.addEventListener('unhandledrejection', function(event) {
            event.preventDefault();
            console.warn('Unhandled promise rejection:', event.reason);
        });

        // General error handler
        window.onerror = function(msg, url, line, col, error) {
            console.warn('Caught error:', msg);
            return false;
        };
        """
        browser.page().runJavaScript(polyfills)

    def inject_video_compatibility_fixes(self, browser):
        fixes = """
        // Video.js compatibility fixes
        if (window.videojs) {
            // Override deprecated extend method
            videojs.extend = function(target, source) {
                return Object.assign(target, source);
            };
            
            // Add default text track cleanup
            const originalAddTrack = videojs.addRemoteTextTrack;
            videojs.addRemoteTextTrack = function(options, manualCleanup) {
                return originalAddTrack.call(this, options, true);
            };
        }

        // Storage API compatibility
        if (window.webkitStorageInfo) {
            console.warn('Using modern storage API');
            window.webkitStorageInfo = {
                queryUsageAndQuota: function(type, success, error) {
                    if (type === window.TEMPORARY) {
                        navigator.webkitTemporaryStorage.queryUsageAndQuota(success, error);
                    } else {
                        navigator.webkitPersistentStorage.queryUsageAndQuota(success, error);
                    }
                }
            };
        }

        // Handle promise timeouts
        const originalPromise = window.Promise;
        window.Promise = function(executor) {
            return new originalPromise((resolve, reject) => {
                const timeoutId = setTimeout(() => {
                    reject(new Error('Promise timed out'));
                }, 30000);  // 30 second timeout

                executor(
                    (value) => {
                        clearTimeout(timeoutId);
                        resolve(value);
                    },
                    (reason) => {
                        clearTimeout(timeoutId);
                        reject(reason);
                    }
                );
            });
        };
        window.Promise.prototype = originalPromise.prototype;
        """
        browser.page().runJavaScript(fixes)

    def inject_media_error_handler(self, browser):
        """Add better media error handling"""
        handler = """
        function handleMediaError(error) {
            if (error.code === 4) {  // MEDIA_ERR_SRC_NOT_SUPPORTED
                console.warn('Media format not supported, attempting fallback...');
                const video = error.target;
                
                // Try different formats
                const formats = ['.mp4', '.webm', '.ogg'];
                const currentSrc = video.src;
                const baseSrc = currentSrc.substring(0, currentSrc.lastIndexOf('.'));
                
                for (const format of formats) {
                    const newSrc = baseSrc + format;
                    if (newSrc !== currentSrc) {
                        video.src = newSrc;
                        video.load();
                        return;
                    }
                }
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const videos = document.getElementsByTagName('video');
            for (let video of videos) {
                video.addEventListener('error', function(e) {
                    handleMediaError(e.target.error);
                });
            }
        });
        """
        browser.page().runJavaScript(handler)

    def enable_indexed_db(self, browser):
        """Enable and fix IndexedDB"""
        fix = """
        // Modern storage handling
        if (!window.storage) {
            window.storage = {
                async get(key) {
                    try {
                        if (navigator.storage && navigator.storage.persist) {
                            await navigator.storage.persist();
                        }
                        return localStorage.getItem(key);
                    } catch (e) {
                        console.warn('Storage error:', e);
                        return null;
                    }
                },
                set(key, value) {
                    try {
                        localStorage.setItem(key, value);
                    } catch (e) {
                        console.warn('Storage error:', e);
                    }
                }
            };
        }
        
        // Handle storage errors
        window.addEventListener('storage', function(e) {
            if (e.storageArea === null) {
                console.warn('Storage quota exceeded');
            }
        });
        """
        browser.page().runJavaScript(fix)

    def handle_js_console(self, level, message, line, source_id):
        """Handle JavaScript console messages"""
        levels = ['Info', 'Warning', 'Error']
        level_name = levels[level] if 0 <= level < len(levels) else 'Unknown'
        
        if level > 0:  # Only log warnings and errors
            print(f"JavaScript {level_name}: {message}")
            print(f"Location: Line {line}, Source: {source_id}")

    def get_search_engine_url(self):
        """Get the homepage URL for the current search engine"""
        url = 'https://www.google.com'  # Default URL
        
        if self.current_search_engine == 'Google':
            url = 'https://www.google.com'
        elif self.current_search_engine == 'Bing':
            url = 'https://www.bing.com'
        elif self.current_search_engine == 'DuckDuckGo':
            url = 'https://duckduckgo.com'
        elif self.current_search_engine == 'Yahoo':
            url = 'https://www.yahoo.com'
        elif self.current_search_engine == 'Ecosia':
            url = 'https://www.ecosia.org'
        
        return QUrl(url)

    def configure_video_settings(self, browser):
        """Configure video-specific settings"""
        settings = browser.page().settings()
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoplayEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        
        # Add media codec support
        browser.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

    def inject_interaction_examples(self, browser):
        examples = """
        // Example 1: Send data to Python
        function sendToPython() {
            window.logToPython('Hello from JavaScript!');
        }

        // Example 2: Get data from Python
        async function getFromPython() {
            const result = await window.processPythonData('test data');
            console.log(result);
        }

        // Example 3: Save data using Python
        function saveThroughPython() {
            window.saveToPython('Data saved at: ' + new Date().toISOString());
        }

        // Example 4: Two-way communication
        async function twoWayExample() {
            console.log('Sending to Python...');
            const processed = await window.processPythonData('hello world');
            console.log('Received from Python:', processed);
        }

        // In browser console or webpage JavaScript:

        // Log to Python
        console.log('This will be logged in Python');

        // Process data through Python
        window.processPythonData('test').then(result => {
            console.log('From Python:', result);
        });

        // Save data using Python
        window.saveToPython('Some data to save');

        // Two-way communication
        async function example() {
            const result = await window.processPythonData('hello');
            console.log(result);  // Will show "Processed by Python: HELLO"
        }
        """
        browser.page().runJavaScript(examples)

    # Add a test method
    def test_python_js_bridge(self):
        self.tabs.currentWidget().page().runJavaScript("""
            // Test JavaScript-Python communication
            sendToPython();
            getFromPython();
            saveThroughPython();
            twoWayExample();
        """)

    def inject_error_handlers(self, browser):
        """Add comprehensive error handling"""
        handlers = """
        // Global error handler
        window.onerror = function(msg, url, line, col, error) {
            if (window.python) {
                python.log(`Error: ${msg} at ${url}:${line}`);
            }
            return false;
        };

        // Promise rejection handler
        window.onunhandledrejection = function(event) {
            if (window.python) {
                python.log(`Unhandled Promise rejection: ${event.reason}`);
            }
        };

        // Console error handler
        const originalError = console.error;
        console.error = function() {
            if (window.python) {
                python.log('Console error: ' + Array.from(arguments).join(' '));
            }
            originalError.apply(console, arguments);
        };
        """
        browser.page().runJavaScript(handlers)

    def setup_video_storage(self, browser):
        # Inject chromestore.js and video handler
        browser.page().runJavaScript("""
            // Initialize video storage
            const videoHandler = new VideoHandler();
            
            // Add video download capability
            async function downloadVideo(videoUrl, filename) {
                try {
                    const fileEntry = await videoHandler.saveVideo(videoUrl, filename);
                    console.log('Video saved:', fileEntry);
                    return fileEntry.toURL();
                } catch (e) {
                    console.error('Error saving video:', e);
                    throw e;
                }
            }

            // Add video playback from storage
            async function playStoredVideo(filename) {
                try {
                    const videoUrl = await videoHandler.getVideoUrl(filename);
                    const video = document.createElement('video');
                    video.src = videoUrl;
                    video.controls = true;
                    document.body.appendChild(video);
                } catch (e) {
                    console.error('Error playing video:', e);
                    throw e;
                }
            }
        """)

    def add_video_controls(self):
        # Add download video button
        download_video_btn = QAction(QIcon('images/download-video.png'), 'Download Video', self)
        download_video_btn.triggered.connect(self.download_current_video)
        # Use self.toolbar instead of navbar
        self.toolbar.addAction(download_video_btn)

        # Add video control buttons
        volume_up_btn = QAction(QIcon('images/volume-up.png'), 'Volume Up', self)
        volume_up_btn.triggered.connect(self.volume_up)
        self.toolbar.addAction(volume_up_btn)

        volume_down_btn = QAction(QIcon('images/volume-down.png'), 'Volume Down', self)
        volume_down_btn.triggered.connect(self.volume_down)
        self.toolbar.addAction(volume_down_btn)

        mute_btn = QAction(QIcon('images/mute.png'), 'Mute', self)
        mute_btn.triggered.connect(self.toggle_mute)
        self.toolbar.addAction(mute_btn)

    def download_current_video(self):
        self.tabs.currentWidget().page().runJavaScript("""
            // Find video element on page
            const video = document.querySelector('video');
            if (video && video.src) {
                const filename = 'video_' + Date.now() + '.mp4';
                downloadVideo(video.src, filename)
                    .then(url => {
                        window.python.log('Video downloaded: ' + url);
                    })
                    .catch(err => {
                        window.python.log('Download error: ' + err);
                    });
            }
        """)

    def volume_up(self):
        """Increase video volume"""
        self.tabs.currentWidget().page().runJavaScript("""
            const videos = document.getElementsByTagName('video');
            for(var i = 0; i < videos.length; i++) {
                videos[i].volume = Math.min(videos[i].volume + 0.1, 1.0);
            }
        """)

    def volume_down(self):
        """Decrease video volume"""
        self.tabs.currentWidget().page().runJavaScript("""
            const videos = document.getElementsByTagName('video');
            for(var i = 0; i < videos.length; i++) {
                videos[i].volume = Math.max(videos[i].volume - 0.1, 0.0);
            }
        """)

    def toggle_mute(self):
        """Toggle video mute state"""
        self.tabs.currentWidget().page().runJavaScript("""
            const videos = document.getElementsByTagName('video');
            for(var i = 0; i < videos.length; i++) {
                videos[i].muted = !videos[i].muted;
            }
        """)

    def inject_video_handler(self, browser):
        """Enhanced video playback handler"""
        video_handler = """
        function enhanceVideoPlayback() {
            // Handle HTML5 video elements
            function setupHTML5Video(video) {
                if (video.hasAttribute('enhanced')) return;
                video.setAttribute('enhanced', 'true');
                
                // Force HTML5 playback
                video.setAttribute('playsinline', '');
                video.setAttribute('webkit-playsinline', '');
                
                // Enable all video formats
                const types = [
                    'video/mp4; codecs="avc1.42E01E, mp4a.40.2"',
                    'video/webm; codecs="vp8, vorbis"',
                    'video/ogg; codecs="theora, vorbis"'
                ];
                types.forEach(type => {
                    const source = document.createElement('source');
                    source.type = type;
                    source.src = video.src;
                    video.appendChild(source);
                });

                // Handle errors
                video.addEventListener('error', function(e) {
                    console.error('Video error:', e);
                    // Try alternative source
                    if (video.src && !video.hasAttribute('tried-fallback')) {
                        video.setAttribute('tried-fallback', 'true');
                        const originalSrc = video.src;
                        // Try different format
                        if (originalSrc.includes('.mp4')) {
                            video.src = originalSrc.replace('.mp4', '.webm');
                        } else if (originalSrc.includes('.webm')) {
                            video.src = originalSrc.replace('.webm', '.mp4');
                        }
                        video.load();
                    }
                });

                // Handle JavaScript video players
                if (window.videojs) {
                    videojs(video, {
                        html5: {
                            vhs: { overrideNative: true },
                            nativeVideoTracks: false,
                            nativeAudioTracks: false,
                            nativeTextTracks: false
                        }
                    });
                }
            }

            // Handle embedded players
            function setupEmbeddedPlayer(iframe) {
                if (iframe.hasAttribute('enhanced')) return;
                iframe.setAttribute('enhanced', 'true');
                
                // Add necessary permissions
                iframe.setAttribute('allow', 'autoplay; fullscreen; encrypted-media');
                
                // Handle common video platforms
                if (iframe.src.includes('youtube.com')) {
                    iframe.src = iframe.src.replace('http://', 'https://');
                    if (!iframe.src.includes('enablejsapi=1')) {
                        iframe.src += (iframe.src.includes('?') ? '&' : '?') + 'enablejsapi=1';
                    }
                }
            }

            // Enhance existing videos
            document.querySelectorAll('video').forEach(setupHTML5Video);
            document.querySelectorAll('iframe').forEach(setupEmbeddedPlayer);

            // Watch for new videos
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeName === 'VIDEO') {
                            setupHTML5Video(node);
                        } else if (node.nodeName === 'IFRAME') {
                            setupEmbeddedPlayer(node);
                        }
                    });
                });
            });

            observer.observe(document.documentElement, {
                childList: true,
                subtree: true
            });
        }

        // Run enhancement when page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', enhanceVideoPlayback);
        } else {
            enhanceVideoPlayback();
        }
        """
        browser.page().runJavaScript(video_handler)

def main():
    try:
        # Create QApplication first
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Then set application attributes
        app.setApplicationName("ZiBrowser")
        app.setOrganizationName("ZiBrowser")
        app.setOrganizationDomain("zibrowser.com")
        
        # Set High DPI support after QApplication creation
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Initialize browser window with error handling
        try:
            window = Browser()
            window.show()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to create browser window: {str(e)}")
            return 1
            
        # Start event loop with exception handling
        return app.exec_()
        
    except Exception as e:
        print(f"Critical error starting ZiBrowser: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
