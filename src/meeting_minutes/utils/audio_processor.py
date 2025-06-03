"""
Audio processing utilities for Meeting Minutes Agent.
"""

import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Generator, List, Tuple

from pydub import AudioSegment
from pydub.utils import make_chunks

from ..config.app_config import PROCESSING_CONFIG
from .logger import setup_logger

logger = setup_logger(__name__)


class AudioProcessor:
    """Handles audio file processing and chunking."""

    def __init__(self):
        self.config = PROCESSING_CONFIG["audio"]
        self.chunk_length_ms = self.config["chunk_length_ms"]
        self.supported_formats = self.config["supported_formats"]
        self.max_file_size_mb = self.config["max_file_size_mb"]

    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate audio file format and size.

        Args:
            file_path: Path to audio file

        Returns:
            True if valid, False otherwise
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            logger.error(f"Audio file not found: {file_path}")
            return False

        # Check file extension
        if path.suffix.lower().lstrip(".") not in self.supported_formats:
            logger.error(f"Unsupported audio format: {path.suffix}")
            return False

        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            logger.warning(f"Large audio file: {file_size_mb:.1f}MB")

        return True

    def load_audio(self, file_path: str) -> AudioSegment:
        """
        Load audio file with format detection.

        Args:
            file_path: Path to audio file

        Returns:
            AudioSegment object

        Raises:
            ValueError: If file cannot be loaded
        """
        if not self.validate_audio_file(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")

        path = Path(file_path)
        format_name = path.suffix.lower().lstrip(".")

        try:
            logger.info(f"Loading audio file: {file_path} (format: {format_name})")
            audio = AudioSegment.from_file(file_path, format=format_name)
            logger.info(f"Audio loaded: {len(audio)/1000:.1f}s duration")
            return audio
        except Exception as e:
            logger.error(f"Failed to load audio file: {e}")
            raise ValueError(f"Cannot load audio file: {e}")

    def create_chunks(self, audio: AudioSegment) -> List[AudioSegment]:
        """
        Split audio into chunks for processing.

        Args:
            audio: AudioSegment to chunk

        Returns:
            List of audio chunks
        """
        chunks = make_chunks(audio, self.chunk_length_ms)
        logger.info(
            f"Created {len(chunks)} chunks of {self.chunk_length_ms/1000}s each"
        )
        return chunks

    def chunk_generator(
        self, file_path: str
    ) -> Generator[Tuple[int, BytesIO], None, None]:
        """
        Generator that yields audio chunks as BytesIO objects.

        Args:
            file_path: Path to audio file

        Yields:
            Tuple of (chunk_index, chunk_audio_data)
        """
        audio = self.load_audio(file_path)
        chunks = self.create_chunks(audio)

        for i, chunk in enumerate(chunks):
            temp_file_path = None
            try:
                # Create temporary file for chunk
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp_file:
                    temp_file_path = temp_file.name
                    chunk.export(temp_file_path, format="wav")

                # Read as BytesIO - ensure file is closed before cleanup
                with open(temp_file_path, "rb") as f:
                    audio_data = BytesIO(f.read())

                yield i, audio_data

            finally:
                # Cleanup temp file if configured and path exists
                if (
                    temp_file_path
                    and PROCESSING_CONFIG["transcription"]["cleanup_temp_files"]
                    and os.path.exists(temp_file_path)
                ):
                    try:
                        os.unlink(temp_file_path)
                    except (PermissionError, OSError) as e:
                        logger.warning(
                            f"Could not delete temporary file {temp_file_path}: {e}"
                        )

    def get_audio_info(self, file_path: str) -> dict:
        """
        Get audio file information.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with audio information
        """
        if not self.validate_audio_file(file_path):
            return {}

        audio = self.load_audio(file_path)

        return {
            "duration_seconds": len(audio) / 1000,
            "duration_formatted": f"{len(audio) // 60000}:{(len(audio) % 60000) // 1000:02d}",
            "sample_rate": audio.frame_rate,
            "channels": audio.channels,
            "bit_depth": audio.sample_width * 8,
            "file_size_mb": Path(file_path).stat().st_size / (1024 * 1024),
            "estimated_chunks": len(self.create_chunks(audio)),
        }
