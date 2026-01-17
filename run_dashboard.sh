#!/bin/bash
# Script to run the Streamlit monitoring dashboard

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Book API Monitoring Dashboard..."
echo "📊 Dashboard will be available at: http://localhost:8501"
echo ""

# Check if we're in a virtual environment or use the one in parent dir
if [ -f "../.venv/bin/streamlit" ]; then
    ../.venv/bin/streamlit run monitoring/dashboard.py
elif [ -f ".venv/bin/streamlit" ]; then
    .venv/bin/streamlit run monitoring/dashboard.py
elif command -v streamlit &> /dev/null; then
    streamlit run monitoring/dashboard.py
else
    echo "❌ Error: Streamlit not found!"
    echo "Please install it with: pip install streamlit==1.40.2"
    exit 1
fi
