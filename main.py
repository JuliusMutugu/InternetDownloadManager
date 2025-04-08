import flet as ft
from IdmCore import DownloadManager
from time import time


class DownloadApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.download_manager = DownloadManager(ffmpeg_path=ffmpeg_path)
        self.create_ui()
        self.download_start_time = None
        self.last_update_time = 0

    def theme_changed(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        self.page.update()



    def setup_page(self):
        self.page.title = "All Social's Download Manager"
        self.page.window.width = 400
        self.page.window.height = 700
        self.page.window.resizable = True
        self.page.theme_mode = 'dark'
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"

    def create_ui(self):

        self.c = ft.Switch(
            on_change=self.theme_changed,
            height = 30,

        )
        # self.c.label = "Light theme" if self.page.theme_mode == ft.ThemeMode.LIGHT else "Dark theme"

        self.app_bar = ft.AppBar(
            leading = ft.IconButton(icon=ft.Icons.MENU),
            title = ft.Text("Download Manager"),
            actions=[
                self.c,
            ]
        )
        self.url_input = ft.TextField(
            label="Paste Video URL here ",
            expand=True,
            border_color=ft.colors.BLUE_400
        )

        self.format_dropdown = ft.Dropdown(
            label="Output Format",
            options=[
                ft.dropdown.Option("MP4"),
                ft.dropdown.Option("MKV"),
                ft.dropdown.Option("WebM"),
                ft.dropdown.Option("FLV"),
                ft.dropdown.Option("MP3"),
            ],
            value="MP4",
            width=100,
            bgcolor=ft.colors.GREY,

        )

        self.status_text = ft.Text(
            " Ready to download",
            size=18,
            color=ft.colors.GREEN
        )
        self.sized_box = ft.Container(
            height = 100,
        )

        # Enhanced progress display
        self.progress_bar = ft.ProgressBar(
            width=500,
            height=20,
            visible=False,
            color=ft.colors.BLUE,
            bgcolor=ft.colors.GREY
        )

        self.progress_text = ft.Text(
            "",
            size=12,
            color=ft.colors.GREY
        )

        self.speed_text = ft.Text(
            "",
            size=12,
            color=ft.colors.GREY
        )

        self.time_remaining_text = ft.Text(
            "",
            size=12,
            color=ft.colors.GREY
        )

        self.download_btn = ft.ElevatedButton(
            "Download",
            icon=ft.icons.DOWNLOAD,
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            height=45,
            on_click=self.on_download_click
        )

        # Layout
        self.page.add(
            self.app_bar,
        )
        self.page.add(
            ft.Column(
                controls = [
                    ft.Text("All Social Media Downloader ",
                            size=24, weight=ft.FontWeight.BOLD,font_family="Comics"),
                    ft.Row(
                        [self.url_input, self.format_dropdown],
                        spacing=10
                    ),
                    self.download_btn,
                    self.progress_bar,
                    ft.Row([self.progress_text, self.speed_text, self.time_remaining_text],
                           spacing=20),
                    self.status_text,
                    self.sized_box,
                    ft.Row(
                        [
                            ft.Icon(name=ft.Icons.FACEBOOK, color=ft.colors.BLUE),
                            ft.Icon(name=ft.Icons.TIKTOK_ROUNDED, color=ft.colors.BLUE),
                            ft.Icon(name=ft.Icons.SOCIAL_DISTANCE_SHARP, color=ft.colors.BLUE)
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment = ft.MainAxisAlignment.CENTER,
                    ),

                    ft.Text("Supports YouTube, TikTok, Instagram, etc.",
                            size=12, color=ft.colors.RED)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            )
        )

    def on_download_click(self, e):
        url = self.url_input.value.strip()
        if not url:
            self.update_status("❌ Please enter a URL", ft.colors.RED)
            return

        output_format = self.download_manager.output_formats.get(
            self.format_dropdown.value, "mp4"
        )

        self.update_status(f"⏳ Starting download...", ft.colors.BLUE)
        self.progress_bar.visible = True
        self.download_btn.disabled = True
        self.download_start_time = time()
        self.last_update_time = 0
        self.page.update()

        # For tracking download speed
        self.last_bytes = 0
        self.last_time = time()

        def progress_hook(d):
            current_time = time()

            if d['status'] == 'downloading':
                # Update progress bar
                if d.get('total_bytes'):
                    progress = float(d['downloaded_bytes']) / float(d['total_bytes'])
                    self.progress_text.value = (
                        f"{progress * 100:.1f}% "
                        f"({d['downloaded_bytes'] / 1e6:.1f}MB / {d['total_bytes'] / 1e6:.1f}MB)"
                    )
                else:
                    progress = 0
                    self.progress_text.value = f"Downloading... ({d['downloaded_bytes'] / 1e6:.1f}MB)"

                self.progress_bar.value = progress

                # Calculate download speed (only update every 0.5 seconds for smoothness)
                if current_time - self.last_update_time > 0.5:
                    elapsed = current_time - self.last_time
                    bytes_diff = d['downloaded_bytes'] - self.last_bytes
                    speed = bytes_diff / elapsed  # bytes per second

                    if speed > 1e6:  # MB/s
                        self.speed_text.value = f"Speed: {speed / 1e6:.1f} MB/s"
                    else:  # KB/s
                        self.speed_text.value = f"Speed: {speed / 1e3:.1f} KB/s"

                    # Calculate time remaining
                    if progress > 0:
                        remaining_bytes = d.get('total_bytes', 0) - d['downloaded_bytes']
                        if speed > 0:
                            remaining_time = remaining_bytes / speed
                            mins, secs = divmod(remaining_time, 60)
                            self.time_remaining_text.value = (
                                f"Remaining: {int(mins)}m {int(secs)}s"
                            )

                    self.last_bytes = d['downloaded_bytes']
                    self.last_time = current_time
                    self.last_update_time = current_time

                self.page.update()

            elif d['status'] == 'finished':
                self.progress_bar.value = 1.0
                self.progress_text.value = "Processing..."
                self.page.update()

        result = self.download_manager.download_video(
            url,
            output_format=output_format,
            progress_hook=progress_hook
        )

        if result['status'] == 'success':
            total_time = time() - self.download_start_time
            mins, secs = divmod(total_time, 60)
            self.update_status(
                f"✅ Download completed in {int(mins)}m {int(secs)}s",
                ft.colors.GREEN
            )
            self.progress_text.value = (
                f"Saved: {result['title']}.{result['format']}"
            )
            self.speed_text.value = ""
            self.time_remaining_text.value = ""
        else:
            self.update_status(
                f"❌ Error: {result['message']}",
                ft.colors.RED
            )

        self.progress_bar.visible = False
        self.download_btn.disabled = False
        self.page.update()

    def update_status(self, message, color):
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()


def main(page: ft.Page):
    DownloadApp(page)

if __name__ == '__main__':
    ft.app(target=main, assets_dir='/assets')