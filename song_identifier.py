import os
import requests
import subprocess
from typing import List, Dict, Optional
import time


class SongIdentifier:
    """Identifies songs in audio files using AudD API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.audd.io/"

    def get_audio_duration(self, audio_path: str) -> int:
        """Get duration of audio file in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-i', audio_path,
                '-show_entries', 'format=duration',
                '-v', 'quiet', '-of', 'csv=p=0'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return int(float(result.stdout.strip()))
        except Exception as e:
            print(f"Error getting duration: {e}")
            return 0

    def analyze_audio_segment(self, audio_path: str, start_time: int, duration: int = 10) -> Optional[Dict]:
        """
        Analyze a segment of audio to identify the song

        Args:
            audio_path: Path to audio file
            start_time: Start time in seconds
            duration: Duration of segment to analyze (default 10s)

        Returns:
            Dict with song info or None if not identified
        """
        try:
            # Extract segment using ffmpeg
            temp_file = f"temp_segment_{start_time}.mp3"

            cmd = [
                'ffmpeg', '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-acodec', 'libmp3lame',
                '-y',  # Overwrite without asking
                temp_file
            ]

            subprocess.run(cmd, capture_output=True, check=True)

            # Send to AudD API
            with open(temp_file, 'rb') as f:
                data = {'api_token': self.api_key}
                files = {'file': f}
                response = requests.post(self.base_url, data=data, files=files)

            # Clean up temp file
            os.remove(temp_file)

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and result.get('result'):
                    return result['result']

            return None

        except Exception as e:
            print(f"Error analyzing segment at {start_time}s: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return None

    def analyze_dj_set(self, audio_path: str, interval: int = 30) -> List[Dict]:
        """
        Analyze entire DJ set by sampling at intervals

        Args:
            audio_path: Path to DJ set audio file
            interval: Seconds between samples (default 30)

        Returns:
            List of identified songs with timestamps
        """
        duration_seconds = self.get_audio_duration(audio_path)

        if duration_seconds == 0:
            print("Error: Could not determine audio duration")
            return []

        songs = []
        current_song = None
        song_start_time = 0

        print(f"Analyzing {duration_seconds} seconds of audio...")

        for time_pos in range(0, duration_seconds, interval):
            print(f"Analyzing at {time_pos}s / {duration_seconds}s...")

            song_info = self.analyze_audio_segment(audio_path, time_pos)

            if song_info:
                song_name = f"{song_info.get('artist', 'Unknown Artist')} - {song_info.get('title', 'Unknown Title')}"

                # New song detected
                if current_song != song_name:
                    # Save previous song if exists
                    if current_song:
                        songs.append({
                            'start': song_start_time,
                            'end': time_pos - 1,
                            'name': current_song
                        })

                    current_song = song_name
                    song_start_time = time_pos

            # Rate limiting - AudD free tier allows 1 request per second
            time.sleep(1)

        # Add the last song
        if current_song:
            songs.append({
                'start': song_start_time,
                'end': duration_seconds,
                'name': current_song
            })

        return songs

    def format_timestamp(self, seconds: int) -> str:
        """Convert seconds to M:SS format"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    def format_tracklist(self, songs: List[Dict]) -> str:
        """Format song list as YouTube-style timestamps"""
        output = "TIMESTAMPS:\n\n"

        for song in songs:
            start = self.format_timestamp(song['start'])
            end = self.format_timestamp(song['end'])
            output += f"{start} - {end} - {song['name']}\n"

        return output


# Alternative: ACRCloud implementation (more accurate but requires more setup)
class ACRCloudIdentifier:
    """Identifies songs using ACRCloud API"""

    def __init__(self, access_key: str, access_secret: str, host: str):
        self.access_key = access_key
        self.access_secret = access_secret
        self.host = host
        # Implementation would require acrcloud SDK
        # pip install pyacrcloud
        pass
