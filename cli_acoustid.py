#!/usr/bin/env python3
"""Test with AcoustID (free, no API key)"""
import sys
import os
from acoustid_identifier import AcoustIDIdentifier


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli_acoustid.py <audio_file> [interval]")
        sys.exit(1)

    audio_path = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 45

    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    print(f"\n🎵 Analyzing with AcoustID: {audio_path}")
    print(f"Interval: {interval}s\n")

    identifier = AcoustIDIdentifier()
    songs = identifier.analyze_dj_set(audio_path, interval=interval)

    print("\n" + "="*60)
    tracklist = identifier.format_tracklist(songs)
    print(tracklist)
    print("="*60)

    if songs:
        output_file = audio_path.rsplit('.', 1)[0] + '_tracklist.txt'
        with open(output_file, 'w') as f:
            f.write(tracklist)
        print(f"\n✅ Saved to: {output_file}")
    else:
        print("\n⚠️  No songs identified. Try:")
        print("  - Longer interval (60-90s)")
        print("  - Different sections of the mix")
        print("  - More mainstream tracks")


if __name__ == '__main__':
    main()
