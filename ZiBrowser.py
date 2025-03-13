import sys
from PyQt5.QtCore import *
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebEngineCore import *
import os

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

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

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

        settings_btn.setMenu(settings_menu)
        navbar.addWidget(settings_btn)

        self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')

        # Download manager
        self.downloads_list = QListWidget()
        self.downloads_list.setWindowTitle("Downloads")
        self.downloads_list.setFixedSize(400, 300)

        # Setup tab suspender
        self.setup_tab_suspender()

        # Setup performance profiles
        self.setup_performance_profiles()

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None or not isinstance(qurl, QUrl):
            qurl = QUrl('')

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

        # Inject JavaScript polyfill for replaceAll
        browser.page().runJavaScript("""
            if (!String.prototype.replaceAll) {
                String.prototype.replaceAll = function(search, replacement) {
                    var target = this;
                    return target.split(search).join(replacement);
                };
            }
        """)

        # Create and set the ad blocker
        ad_blocker = AdBlocker()
        browser.page().profile().setUrlRequestInterceptor(ad_blocker)

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
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_url(qurl)
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
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
        private_profile = QWebEngineProfile()
        private_profile.setOffTheRecord(True)
        
        private_window = Browser()
        private_window.setWindowTitle("ZiBrowser (Private Mode)")
        private_window.profile = private_profile
        
        # Set a different color scheme for private windows
        private_window.setStyleSheet("QMainWindow { background-color: #2b0b3f; }")
        private_window.show()

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

app = QApplication(sys.argv)
QApplication.setApplicationName("ZiBrowser")
window = Browser()
window.show()
app.exec_()
