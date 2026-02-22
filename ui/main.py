"""
ApplyAI - Smart Job Application Assistant
Main Entry Point
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use modern GUI
from ui.gui_modern import ApplyAI

if __name__ == "__main__":
    app = ApplyAI()
    app.mainloop()
