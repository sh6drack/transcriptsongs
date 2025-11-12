#!/usr/bin/env python3
"""
Command-line interface using Shazam for better accuracy
Usage: python cli_shazam.py path/to/djset.mp3
"""

import sys
import os
from shazam_identifier import ShazamIdentifier


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli_shazam.py <audio_file_path> [interval_seconds]")
        print("Example: python cli_shazam.py my_djset.mp3 30")
        sys.exit(1)

    audio_path = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    print(f"\n🎵 Analyzing with Shazam: {audio_path}")
    print(f"Sampling interval: {interval} seconds\n")

    identifier = ShazamIdentifier()
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
