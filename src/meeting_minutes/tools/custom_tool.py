import json
from pathlib import Path
from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class TextSummarizerInput(BaseModel):
    """Input schema for TextSummarizerTool."""

    text: str = Field(..., description="The text content to summarize")
    max_sentences: int = Field(
        default=5, description="Maximum number of sentences in summary"
    )
    focus_keywords: Optional[str] = Field(
        default=None, description="Comma-separated keywords to focus on"
    )


class TextSummarizerTool(BaseTool):
    name: str = "Text Summarizer"
    description: str = (
        "Summarizes long text content into key points. Useful for condensing meeting transcripts, "
        "documents, or other lengthy text into concise summaries. Can focus on specific keywords if provided."
    )
    args_schema: Type[BaseModel] = TextSummarizerInput

    def _run(
        self, text: str, max_sentences: int = 5, focus_keywords: Optional[str] = None
    ) -> str:
        """
        Summarize text content into key points.

        Args:
            text: Text to summarize
            max_sentences: Maximum sentences in summary
            focus_keywords: Keywords to focus on (comma-separated)

        Returns:
            Summarized text
        """
        try:
            logger.info(f"Summarizing text of {len(text)} characters")

            # Basic text processing
            sentences = [s.strip() for s in text.split(".") if s.strip()]

            if len(sentences) <= max_sentences:
                logger.info("Text is already concise enough")
                return text

            # Simple scoring based on sentence length and keyword presence
            scored_sentences = []
            keywords = (
                [k.strip().lower() for k in (focus_keywords or "").split(",")]
                if focus_keywords
                else []
            )

            for sentence in sentences:
                score = len(sentence.split())  # Base score on word count

                # Boost score for keyword presence
                if keywords:
                    for keyword in keywords:
                        if keyword in sentence.lower():
                            score += 10

                scored_sentences.append((score, sentence))

            # Sort by score and take top sentences
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            top_sentences = [sent for _, sent in scored_sentences[:max_sentences]]

            # Reconstruct in original order
            summary_sentences = []
            for sentence in sentences:
                if sentence in top_sentences:
                    summary_sentences.append(sentence)

            summary = ". ".join(summary_sentences) + "."
            logger.info(f"Generated summary with {len(summary_sentences)} sentences")

            return summary

        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return f"Error generating summary: {str(e)}"


class FileMetadataExtractorInput(BaseModel):
    """Input schema for FileMetadataExtractorTool."""

    file_path: str = Field(..., description="Path to the file to analyze")


class FileMetadataExtractorTool(BaseTool):
    name: str = "File Metadata Extractor"
    description: str = (
        "Extracts metadata and basic information from files. Useful for analyzing "
        "audio files, documents, and other file types in the meeting minutes workflow."
    )
    args_schema: Type[BaseModel] = FileMetadataExtractorInput

    def _run(self, file_path: str) -> str:
        """
        Extract metadata from a file.

        Args:
            file_path: Path to file

        Returns:
            JSON string with file metadata
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return json.dumps({"error": f"File not found: {file_path}"})

            # Basic file information
            stat = path.stat()
            metadata = {
                "file_name": path.name,
                "file_extension": path.suffix,
                "file_size_bytes": stat.st_size,
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
            }

            # Audio file specific metadata
            if path.suffix.lower() in [".wav", ".mp3", ".m4a", ".flac"]:
                try:
                    from ..utils.audio_processor import AudioProcessor

                    processor = AudioProcessor()
                    audio_info = processor.get_audio_info(file_path)
                    metadata.update({"audio_info": audio_info})
                except Exception as e:
                    metadata["audio_error"] = str(e)

            logger.info(f"Extracted metadata for: {file_path}")
            return json.dumps(metadata, indent=2)

        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return json.dumps({"error": f"Failed to extract metadata: {str(e)}"})


# Legacy tool for backward compatibility
class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    argument: str = Field(..., description="Description of the argument.")


class MyCustomTool(BaseTool):
    name: str = "Legacy Custom Tool"
    description: str = "Legacy tool maintained for backward compatibility."
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        return f"Legacy tool processed: {argument}"
