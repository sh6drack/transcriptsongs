#!/usr/bin/env python3
"""
Command-line interface for analyzing DJ sets
Usage: python cli.py path/to/djset.mp3
"""

import sys
import os
from dotenv import load_dotenv
from song_identifier import SongIdentifier


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python cli.py <audio_file_path> [interval_seconds]")
        print("Example: python cli.py my_djset.mp3 30")
        sys.exit(1)

    audio_path = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    api_key = os.getenv('AUDD_API_KEY')
    if not api_key:
        print("Error: AUDD_API_KEY not found in .env file")
        print("Please add your API key. Get one at: https://audd.io/")
        sys.exit(1)

    print(f"\n🎵 Analyzing: {audio_path}")
    print(f"Sampling interval: {interval} seconds\n")

    identifier = SongIdentifier(api_key)
    songs = identifier.analyze_dj_set(audio_path, interval=interval)

    print("\n" + "="*60)
    print(identifier.format_tracklist(songs))
    print("="*60)

    # Save to file
    output_file = audio_path.rsplit('.', 1)[0] + '_tracklist.txt'
    with open(output_file, 'w') as f:
        f.write(identifier.format_tracklist(songs))

    print(f"\n✅ Tracklist saved to: {output_file}")


if __name__ == '__main__':
    main()
