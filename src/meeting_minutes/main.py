#!/usr/bin/env python

# Add Self type patch before importing crewai
import os
import sys
import typing

from typing_extensions import Self

if not hasattr(typing, "Self"):
    typing.Self = Self
    sys.modules["typing"].Self = Self

# Load environment variables first, before any imports
from dotenv import load_dotenv

load_dotenv()

from pathlib import Path

from crewai.flow.flow import Flow, listen, start
from elevenlabs import ElevenLabs

# Now we can safely import from crewai
from pydantic import BaseModel

# Important: Apply monkey patches before importing CrewAI components
from meeting_minutes.utils.monkey_patches import apply_monkey_patches

apply_monkey_patches()

from meeting_minutes.config.app_config import API_CONFIG, validate_environment
from meeting_minutes.crews.gmailcrew.gmailcrew import GmailCrew
from meeting_minutes.crews.meeting_minutes_crew.meeting_minutes_crew import (
    MeetingMinutesCrew,
)
from meeting_minutes.utils.audio_processor import AudioProcessor
from meeting_minutes.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Initialize Eleven Labs client
eleven_api_key = os.getenv("ELEVENLABS_API_KEY", os.getenv("ELEVEN_LABS_API_KEY"))
if not eleven_api_key:
    logger.error("ElevenLabs API key not found in environment variables")
    raise ValueError("ElevenLabs API key is required")

eleven_labs = ElevenLabs(api_key=eleven_api_key)
audio_processor = AudioProcessor()


class MeetingMinutesState(BaseModel):
    transcript: str = ""
    meeting_minutes: str = ""
    audio_info: dict = {}


class MeetingMinutesFlow(Flow[MeetingMinutesState]):
    @start()
    def transcribe_meeting(self):
        """Transcribe meeting audio using ElevenLabs API."""
        logger.info("Starting meeting transcription")

        SCRIPT_DIR = Path(__file__).parent
        audio_path = str(SCRIPT_DIR / "EarningsCall.wav")

        # Validate audio file
        if not audio_processor.validate_audio_file(audio_path):
            error_msg = f"Invalid or missing audio file: {audio_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Get audio information
        audio_info = audio_processor.get_audio_info(audio_path)
        self.state.audio_info = audio_info
        logger.info(
            f"Processing audio: {audio_info.get('duration_formatted', 'unknown')} duration"
        )

        # Process audio in chunks
        full_transcription = ""
        chunk_count = 0
        failed_chunks = 0

        try:
            for chunk_index, audio_data in audio_processor.chunk_generator(audio_path):
                chunk_count += 1
                logger.info(
                    f"Transcribing chunk {chunk_count}/{audio_info.get('estimated_chunks', '?')}"
                )

                try:
                    # Use ElevenLabs for transcription
                    transcription = eleven_labs.speech_to_text.convert(
                        file=audio_data,
                        model_id=API_CONFIG["elevenlabs"]["model_id"],
                        tag_audio_events=API_CONFIG["elevenlabs"]["tag_audio_events"],
                        diarize=API_CONFIG["elevenlabs"]["diarize"],
                    )

                    chunk_text = transcription.text.strip()
                    if chunk_text:
                        full_transcription += chunk_text + " "
                        logger.debug(
                            f"Chunk {chunk_count} transcribed: {len(chunk_text)} characters"
                        )

                except Exception as e:
                    failed_chunks += 1
                    logger.error(f"Failed to transcribe chunk {chunk_count}: {e}")
                    # Continue with next chunk
                    continue

        except Exception as e:
            logger.error(f"Fatal error during transcription: {e}")
            raise

        # Finalize transcription
        self.state.transcript = full_transcription.strip()

        logger.info(f"Transcription completed:")
        logger.info(f"  - Total chunks: {chunk_count}")
        logger.info(f"  - Failed chunks: {failed_chunks}")
        logger.info(f"  - Transcript length: {len(self.state.transcript)} characters")

        if not self.state.transcript:
            raise ValueError("No transcription generated from audio file")

    @listen(transcribe_meeting)
    def generate_meeting_minutes(self):
        """Generate structured meeting minutes from transcript."""
        logger.info("Generating meeting minutes")

        if not self.state.transcript:
            logger.error("No transcript available for meeting minutes generation")
            raise ValueError("Transcript is required for meeting minutes generation")

        try:
            crew = MeetingMinutesCrew()

            inputs = {
                "transcript": self.state.transcript,
                "audio_info": self.state.audio_info,
            }

            logger.info("Starting CrewAI meeting minutes generation")
            meeting_minutes = crew.crew().kickoff(inputs)

            self.state.meeting_minutes = str(meeting_minutes)
            logger.info(
                f"Meeting minutes generated: {len(self.state.meeting_minutes)} characters"
            )

        except Exception as e:
            logger.error(f"Failed to generate meeting minutes: {e}")
            raise

    @listen(generate_meeting_minutes)
    def create_draft_meeting_minutes(self):
        """Create Gmail draft with meeting minutes."""
        logger.info("Creating Gmail draft")

        if not self.state.meeting_minutes:
            logger.error("No meeting minutes available for draft creation")
            raise ValueError("Meeting minutes are required for draft creation")

        try:
            crew = GmailCrew()

            inputs = {
                "body": str(self.state.meeting_minutes),
                "audio_info": self.state.audio_info,
            }

            logger.info("Starting Gmail draft creation")
            draft_result = crew.crew().kickoff(inputs)

            logger.info(f"Gmail draft created successfully: {draft_result}")

        except Exception as e:
            logger.error(f"Failed to create Gmail draft: {e}")
            raise


def kickoff():
    """Main entry point for the meeting minutes flow."""
    logger.info("Starting Meeting Minutes Agent")

    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed")
        return False

    # Disable agentops integration to skip authentication during crew kickoff
    try:
        import agentops

        agentops.init = lambda *args, **kwargs: None
        logger.info("AgentOps integration disabled")
    except ImportError:
        logger.debug("AgentOps not installed")

    try:
        meeting_minutes_flow = MeetingMinutesFlow()

        # Generate flow visualization
        try:
            meeting_minutes_flow.plot()
            logger.info("Flow diagram generated")
        except Exception as e:
            logger.warning(f"Could not generate flow diagram: {e}")

        # Execute the flow
        logger.info("Executing meeting minutes flow")
        meeting_minutes_flow.kickoff()

        logger.info("Meeting minutes flow completed successfully")
        return True

    except Exception as e:
        logger.error(f"Meeting minutes flow failed: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = kickoff()
    exit_code = 0 if success else 1
    logger.info(f"Application exiting with code: {exit_code}")
    sys.exit(exit_code)
