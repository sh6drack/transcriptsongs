import os
import subprocess
import acoustid
from typing import List, Dict, Optional
import time


class AcoustIDIdentifier:
    """Identifies songs using AcoustID/MusicBrainz (free, no API key needed)"""

    def __init__(self):
        # AcoustID public API key (free for non-commercial use)
        self.api_key = '8XaBELgH'

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
        """Analyze a segment using AcoustID"""
        try:
            # Extract segment
            temp_file = f"temp_segment_{start_time}.mp3"

            cmd = [
                'ffmpeg', '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-acodec', 'libmp3lame',
                '-y',
                temp_file
            ]

            subprocess.run(cmd, capture_output=True, check=True)

            # Try to match with AcoustID
            try:
                results = acoustid.match(self.api_key, temp_file)

                for score, recording_id, title, artist in results:
                    if score > 0.5:  # Good enough match
                        os.remove(temp_file)
                        return {
                            'artist': artist,
                            'title': title,
                            'score': score
                        }
            except acoustid.NoBackendError:
                print("Error: fpcalc not found. Install with: brew install chromaprint")
                os.remove(temp_file)
                return None
            except Exception as e:
                print(f"AcoustID error at {start_time}s: {e}")

            os.remove(temp_file)
            return None

        except Exception as e:
            print(f"Error at {start_time}s: {e}")
            if os.path.exists(f"temp_segment_{start_time}.mp3"):
                os.remove(f"temp_segment_{start_time}.mp3")
            return None

    def analyze_dj_set(self, audio_path: str, interval: int = 30) -> List[Dict]:
        """Analyze entire DJ set"""
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

            time.sleep(0.5)  # Rate limiting

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
