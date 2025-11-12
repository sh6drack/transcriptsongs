#!/usr/bin/env python3
import sys
import os
from shazam_simple import SimpleShazam


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_shazam.py <audio_file> [interval_seconds]")
        sys.exit(1)

    audio_path = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 45

    if not os.path.exists(audio_path):
        print(f"❌ File not found: {audio_path}")
        sys.exit(1)

    print(f"\n🎵 ShazamIO DJ Set Analyzer")
    print(f"📁 File: {os.path.basename(audio_path)}")
    print(f"⏱️  Interval: {interval}s\n")
    print("="*60 + "\n")

    shazam = SimpleShazam()
    songs = shazam.analyze_dj_set(audio_path, interval=interval)

    print("\n" + "="*60)
    tracklist = shazam.format_tracklist(songs)
    print(tracklist)
    print("="*60)

    if songs:
        output_file = audio_path.rsplit('.', 1)[0] + '_tracklist.txt'
        with open(output_file, 'w') as f:
            f.write(tracklist)
        print(f"\n✅ Saved to: {output_file}")
    else:
        print("\n⚠️  No songs found. Your tracks may be:")
        print("   - Underground/unreleased")
        print("   - Heavily mixed/edited")
        print("   - Not in Shazam's database")


if __name__ == '__main__':
    main()
