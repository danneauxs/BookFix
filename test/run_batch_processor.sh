#!/bin/bash
# Run Bookfix Batch Processor - Gradio Web App

cd /home/danno/MyApps/Bookfix

# Activate virtual environment
source venv/bin/activate

# Check if input_text directory exists
if [ ! -d "input_text" ]; then
    echo "ERROR: input_text directory not found!"
    echo "Please create input_text/ directory with .txt files to process"
    exit 1
fi

# Check if .txt files exist
if [ -z "$(ls input_text/*.txt 2>/dev/null)" ]; then
    echo "ERROR: No .txt files found in input_text/"
    exit 1
fi

echo "Starting Bookfix Batch Processor..."
echo "Access at: http://localhost:7898"
echo ""
echo "Files found in input_text/:"
ls -lh input_text/*.txt | awk '{print "  - " $9 " (" $5 ")"}'
echo ""

# Run the app
python3 batch_processor_app.py
