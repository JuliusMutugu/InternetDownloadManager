import yt_dlp
import os
from pathlib import Path

from pytube.cli import ffmpeg_process


class DownloadManager:
    def __init__(self, ffmpeg_path=None):
        self.ffmpeg_path = ffmpeg_path
        self.supported_platforms = {
            "youtube.com": "YouTube",
            "youtu.be": "YouTube",
            "tiktok.com": "TikTok",
            "instagram.com": "Instagram",
            "facebook.com": "Facebook",
            "twitter.com": "Twitter",
            "x.com": "Twitter"
        }
        self.output_formats = {
            "MP4": "mp4",
            "MKV": "mkv",
            "WebM": "webm",
            "FLV": "flv",
            "m4a": "mp4",
            "mp3": "mp3"
        }

    def detect_platform(self, url):
        for domain, platform in self.supported_platforms.items():
            if domain in url:
                return platform
        return "Unknown"

    def download_video(self, url, output_format="mp4", progress_hook=None):
        platform = self.detect_platform(url)
        output_path = os.path.join("downloads", platform)
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': output_format,
            'progress_hooks': [progress_hook] if progress_hook else [],
            'quiet': True,
            'noplaylist': True,

        }

        if self.ffmpeg_path:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_path

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'output_path': output_path,
                    'title': info.get('title', 'video'),
                    'format': output_format
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }