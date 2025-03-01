from pathlib import Path
from typing import Any, Dict, List

from yt_dlp import YoutubeDL

VALID_URLS: List[str] = ["youtube.com", "youtu.be"]


class VideoDownloader:
    @classmethod
    def download(cls, url: str, output_path: str, audio_only: bool = False) -> None:
        """Download a YouTube video using the given URL.
        Args:
            url (str): The URL of the YouTube video.
            output_path (str): The path to save the downloaded video.
            audio_only (bool): If True, only the audio will be downloaded.
        """
        if not any(valid in url.lower() for valid in VALID_URLS):
            raise ValueError("Invalid URL. Only YouTube URLs are supported.")
        output: Path = Path(output_path)
        output.mkdir(parents=True, exist_ok=True)
        options: Dict[str, Any] = cls._get_tool_options(output, audio_only)
        downloader: YoutubeDL = YoutubeDL(options)
        downloader.download([url])

    @classmethod
    def _get_tool_options(cls, output: Path, audio_only: bool) -> Dict[str, Any]:
        template: Dict[str, Any] = {
            "outtmpl": f"{output}/%(title)s.%(ext)s",  # Output template
        }
        if not audio_only:
            return {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",  # Video+Audio format combination
                "merge_output_format": "mp4",  # Final output format should be MP4
                "postprocessors": [  # Post-processing to merge video and audio
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": "mp4",  # Ensure the final file is MP4
                    }
                ],
                **template,
            }
        return {
            "format": "bestaudio/best",  # Best audio format
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",  # Extract audio using FFmpeg
                    "preferredcodec": "mp3",  # Save as mp3
                    "preferredquality": "192",  # Bitrate
                }
            ],
            **template,
        }
