import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty,BooleanProperty, ListProperty
from kivy.clock import Clock
from time import time
from kivy.core.window import Window
import sys
from IdmCore import DownloadManager


class MainLayout(BoxLayout):
    progress_value = NumericProperty(0)
    progress_text = StringProperty('Ready to download')
    speed_text = StringProperty('')
    time_text = StringProperty('')
    status_text = StringProperty('')
    btn_disabled = BooleanProperty(False)
    btn_text = StringProperty('DOWNLOAD')
    btn_color = ListProperty([0.2, 0.6, 1, 1])
    status_color = ListProperty([0.2, 0.2, 0.2, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_manager = DownloadManager()
        self.download_start_time = None
        self.last_bytes = 0
        self.last_time = 0

    def start_download(self):
        url = self.ids.url_input.text.strip()
        if not url:
            self.update_status('Please enter a URL', [1, 0, 0, 1])
            return

        # Reset UI state
        self.progress_value = 0
        self.progress_text = 'Starting download...'
        self.speed_text = ''
        self.time_text = ''
        self.status_text = ''
        self.btn_disabled = True
        self.btn_text = 'DOWNLOADING...'
        self.btn_color = [0.5, 0.5, 0.5, 1]
        self.download_start_time = time()
        self.last_bytes = 0
        self.last_time = time()

        # Start download (MP4 only)
        Clock.schedule_once(lambda dt: self.do_download(url))

    def do_download(self, url):
        def safe_update(d):
            try:
                if d.get('status') == 'downloading':
                    Clock.schedule_once(lambda dt: self.update_progress(d))
                elif d.get('status') == 'finished':
                    Clock.schedule_once(lambda dt: self.download_complete())
            except Exception as e:
                print(f"Progress update failed: {e}", file=sys.stderr)

        try:
            result = self.download_manager.download_video(
                url,
                progress_hook = safe_update
            )
            if result['status'] == 'error':
                Clock.schedule_once(lambda dt: self.show_error(result['message']))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"System error: {str(e)}"))

    def update_progress(self, d):
        try:
            current_time = time()

            if d.get('total_bytes'):
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_text = (
                    f"Downloading: {progress:.1f}% "
                    f"({d['downloaded_bytes'] / 1e6:.1f}MB / {d['total_bytes'] / 1e6:.1f}MB)"
                )
            else:
                progress = 0
                self.progress_text = f"Downloading... ({d['downloaded_bytes'] / 1e6:.1f}MB)"

            self.progress_value = progress

            # Update speed every 0.5 seconds
            if current_time - self.last_time > 0.5:
                elapsed = current_time - self.last_time
                bytes_diff = d['downloaded_bytes'] - self.last_bytes
                speed = bytes_diff / elapsed  # bytes per second

                if speed > 1e6:  # MB/s
                    self.speed_text = f"Speed: {speed / 1e6:.1f} MB/s"
                else:  # KB/s
                    self.speed_text = f"Speed: {speed / 1e3:.1f} KB/s"

                # Calculate time remaining
                if d.get('total_bytes'):
                    remaining_bytes = d['total_bytes'] - d['downloaded_bytes']
                    if speed > 0:
                        remaining_time = remaining_bytes / speed
                        mins, secs = divmod(remaining_time, 60)
                        self.time_text = f"Time left: {int(mins)}m {int(secs)}s"

                self.last_bytes = d['downloaded_bytes']
                self.last_time = current_time
        except Exception as e:
            print(f"Progress update error: {e}")

    def download_complete(self):
        total_time = time() - self.download_start_time
        mins, secs = divmod(total_time, 60)
        self.update_status(
            f"Download completed in {int(mins)}m {int(secs)}s",
            [0, 0.6, 0, 1]
        )
        self.progress_text = "Download complete!"
        self.progress_value = 100
        self.btn_disabled = False
        self.btn_text = 'DOWNLOAD'
        self.btn_color = [0.2, 0.6, 1, 1]

    def show_error(self, message):
        self.update_status(message, [1, 0, 0, 1])
        self.progress_text = "Download failed"
        self.progress_value = 0
        self.btn_disabled = False
        self.btn_text = 'DOWNLOAD'
        self.btn_color = [0.2, 0.6, 1, 1]

    def update_status(self, message, color):
        self.status_text = message
        self.status_color = color


class YouTubeDownloaderApp(App):
    def build(self):
        Window.clearcolor = (0.96, 0.96, 0.96, 1)
        self.title = 'Media MP4 Downloader'
        self.icon = "assets/icondownload.png"
        try:
            return MainLayout()
        except Exception as e:
            print(f"Fatal startup error: {e}", file=sys.stderr)
            raise


if __name__ == '__main__':
    try:
        YouTubeDownloaderApp().run()

    except Exception as e:
        print(f"Application crashed: {e}", file=sys.stderr)
        input("Press Enter to exit...")