#!/usr/bin/env python3
"""
Fetch YouTube video transcript.

Usage:
    python fetch_youtube.py --url "https://youtube.com/watch?v=VIDEO_ID"
    python fetch_youtube.py --url "VIDEO_ID"
"""

import argparse
import json
import re
import sys
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats or raw ID.

    Supported formats:
    - https://youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    - VIDEO_ID (raw 11-character ID)
    """
    url_or_id = url_or_id.strip()

    # Pattern for YouTube video ID (11 characters, alphanumeric + _ -)
    video_id_pattern = r'^[a-zA-Z0-9_-]{11}$'

    # If it's already a raw video ID
    if re.match(video_id_pattern, url_or_id):
        return url_or_id

    # URL patterns
    patterns = [
        # youtube.com/watch?v=VIDEO_ID
        r'(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})',
        # youtu.be/VIDEO_ID
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        # youtube.com/embed/VIDEO_ID
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        # youtube.com/v/VIDEO_ID
        r'(?:youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        # youtube.com/shorts/VIDEO_ID
        r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return None


def fetch_transcript(video_id: str) -> dict:
    """
    Fetch transcript for a YouTube video.

    Returns a dict with success status and either transcript data or error info.
    """
    ytt_api = YouTubeTranscriptApi()

    try:
        transcript_list = ytt_api.list(video_id)

        # Try to get English transcript first, then any available
        try:
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        except NoTranscriptFound:
            # Get any available transcript
            try:
                transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
            except NoTranscriptFound:
                # Get first available transcript
                transcript = next(iter(transcript_list))
    except NoTranscriptFound:
        return {
            'success': False,
            'error': 'No transcript available for this video',
            'error_code': 'NO_TRANSCRIPT',
        }
    except TranscriptsDisabled:
        return {
            'success': False,
            'error': 'Transcripts are disabled for this video',
            'error_code': 'TRANSCRIPT_DISABLED',
        }
    except VideoUnavailable:
        return {
            'success': False,
            'error': 'Video not found or unavailable',
            'error_code': 'VIDEO_NOT_FOUND',
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Network or API error: {str(e)}',
            'error_code': 'NETWORK_ERROR',
        }

    # Fetch the transcript data
    try:
        fetched = transcript.fetch()
        transcript_data = fetched.to_raw_data()
        full_text = ' '.join(entry['text'] for entry in transcript_data)

        return {
            'success': True,
            'video_id': video_id,
            'url': f'https://youtube.com/watch?v={video_id}',
            'transcript': transcript_data,
            'full_text': full_text,
            'language': transcript.language_code,
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to fetch transcript: {str(e)}',
            'error_code': 'NETWORK_ERROR',
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Fetch YouTube video transcript',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s --url "https://youtu.be/dQw4w9WgXcQ"
  %(prog)s --url "dQw4w9WgXcQ"
        '''
    )
    parser.add_argument(
        '--url',
        required=True,
        help='YouTube URL or video ID'
    )
    parser.add_argument(
        '--output',
        default='json',
        choices=['json'],
        help='Output format (default: json)'
    )

    args = parser.parse_args()

    # Extract video ID
    video_id = extract_video_id(args.url)
    if not video_id:
        result = {
            'success': False,
            'error': f'Could not extract video ID from: {args.url}',
            'error_code': 'INVALID_URL',
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Fetch transcript
    result = fetch_transcript(video_id)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
