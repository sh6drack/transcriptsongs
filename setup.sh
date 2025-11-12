#!/bin/bash

echo "🎵 TranscriptSongs Setup"
echo "======================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Get a free API key from https://audd.io/"
echo "2. Copy .env.example to .env: cp .env.example .env"
echo "3. Add your API key to .env"
echo "4. Run the app: python app.py"
echo ""
echo "Or use the CLI: python cli.py your_djset.mp3"
echo ""
