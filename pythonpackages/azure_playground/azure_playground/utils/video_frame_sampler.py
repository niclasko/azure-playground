import logging
from itertools import chain
from pathlib import Path
from typing import Iterator, List

import cv2
import tqdm
from azure_playground.data_model.frame import Frame
from azure_playground.data_model.video import Video
from azure_playground.utils.filename_sanitizer import FilenameSanitizer


class VideoFrameSampler:
    def __init__(self, input: str, output: str) -> None:
        self.input: Path = Path(input)
        self.output: Path = FilenameSanitizer.sanitize(Path(output) / self.input.name)

        # Set up logging dynamically based on the output directory
        log: Path = self.output / "video_framer.log"
        self.output.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(str(log)),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized. Logs will be saved to {str(log)}")

    def sample(self, samples: int = 10) -> List[Frame]:
        """Sample frames from a video at regular intervals as specified by the number of samples.

        Args:
            samples (int): The number of frames to sample.
        Returns:
            List[Frame]: A list of sampled frames.
        """
        try:
            self._cleanup()
            frames: List[Frame] = list(self._capture(samples))
            metadata: Path = self.output / "metadata.json"
            video: Video = Video(
                name=self.input.name,
                path=self.input,
                frames=frames,
            )
            metadata.write_text(video.model_dump_json(indent=4))
            self.logger.info(f"Metadata written to {metadata}")
        except Exception as e:
            self.logger.error(f"An error occurred while processing the video: {e}")
        return frames

    def _cleanup(self) -> None:
        files: List[Path] = list(chain(self.output.glob("*.jpg"), self.output.glob("*.json")))
        for file in files:
            file.unlink()

    def _capture(self, samples: int) -> Iterator[Frame]:
        video: cv2.VideoCapture = cv2.VideoCapture(str(self.input))
        if not video.isOpened():
            self.logger.error(f"Could not open video file: {self.input}")
            raise ValueError(f"Could not open video file: {self.input}")

        frames: int = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps: float = video.get(cv2.CAP_PROP_FPS)
        seconds: float = frames / fps

        self.logger.info(f"Video '{self.input.name}' has {frames} frames at {fps} FPS.")

        for sample in tqdm.tqdm(range(1, samples + 1), desc="Extracting frames"):
            offset: float = sample / samples * seconds
            file: Path = self.output / f"{offset}.jpg"
            index: int = int(offset * fps)
            video.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = video.read()
            if ret:
                cv2.imwrite(str(file), frame)
                yield Frame(offset=offset, image=file)

        video.release()
        self.logger.info(f"Frame extraction completed. Frames saved to: {self.output}")
