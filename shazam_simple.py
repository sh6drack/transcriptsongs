import os
import subprocess
import asyncio
import json
from typing import List, Dict, Optional
from pathlib import Path


class SimpleShazam:
    """Shazam identifier that bypasses pydub issues"""

    def get_audio_duration(self, audio_path: str) -> int:
        """Get duration of audio file in seconds"""
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

    async def recognize_segment_async(self, segment_path: str) -> Optional[Dict]:
        """Use ShazamIO to recognize a segment"""
        try:
            # Import here to avoid pydub issues on module load
            from shazamio import Shazam

            shazam = Shazam()
            out = await shazam.recognize(segment_path)

            if out and 'track' in out:
                track = out['track']
                return {
                    'artist': track.get('subtitle', 'Unknown Artist'),
                    'title': track.get('title', 'Unknown Title')
                }
            return None
        except Exception as e:
            print(f"Shazam error: {e}")
            return None

    def analyze_audio_segment(self, audio_path: str, start_time: int, duration: int = 12) -> Optional[Dict]:
        """Extract segment and recognize with Shazam"""
        temp_file = f"temp_shazam_{start_time}.mp3"

        try:
            # Extract segment
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-acodec', 'libmp3lame',
                '-ar', '44100',  # Shazam works better with 44.1kHz
                '-ac', '1',      # Mono is fine for recognition
                '-b:a', '128k',
                '-y',
                temp_file
            ]

            result = subprocess.run(cmd, capture_output=True, check=True)

            # Recognize with Shazam
            song_info = asyncio.run(self.recognize_segment_async(temp_file))

            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

            return song_info

        except Exception as e:
            print(f"Error at {start_time}s: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return None

    def analyze_dj_set(self, audio_path: str, interval: int = 45) -> List[Dict]:
        """Analyze DJ set with Shazam"""
        duration_seconds = self.get_audio_duration(audio_path)

        if duration_seconds == 0:
            print("Error: Could not determine audio duration")
            return []

        songs = []
        current_song = None
        song_start_time = 0

        print(f"🎵 Analyzing {duration_seconds // 60} minutes of audio with Shazam...")
        print(f"Checking every {interval} seconds\n")

        for time_pos in range(0, duration_seconds, interval):
            mins = time_pos // 60
            secs = time_pos % 60
            print(f"⏱️  {mins:02d}:{secs:02d} / {duration_seconds // 60}:{duration_seconds % 60:02d}...", end=" ", flush=True)

            song_info = self.analyze_audio_segment(audio_path, time_pos)

            if song_info:
                song_name = f"{song_info['artist']} - {song_info['title']}"
                print(f"✅ {song_name}")

                # New song detected
                if current_song != song_name:
                    # Save previous song
                    if current_song:
                        songs.append({
                            'start': song_start_time,
                            'end': time_pos - 1,
                            'name': current_song
                        })

                    current_song = song_name
                    song_start_time = time_pos
            else:
                print("❌ Not found")

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
        """Format as YouTube timestamps"""
        if not songs:
            return "TIMESTAMPS:\n\n(No songs identified - tracks may not be in Shazam's database)"

        output = "TIMESTAMPS:\n\n"
        for song in songs:
            start = self.format_timestamp(song['start'])
            end = self.format_timestamp(song['end'])
            output += f"{start} - {end} - {song['name']}\n"
        return output
