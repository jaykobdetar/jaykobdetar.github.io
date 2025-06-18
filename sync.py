#!/usr/bin/env python3
"""
Content Sync Tool - Simple Wrapper
==================================
Just runs the actual sync script with subprocess
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the sync script directly via subprocess"""
    # Get project root and script path
    project_root = Path(__file__).parent
    script_path = project_root / "scripts" / "sync_content.py"
    
    # Get command line arguments (default to no args if none provided)
    args = sys.argv[1:]
    
    # Use appropriate Python command for platform
    python_cmd = "python" if sys.platform == "win32" else "python3"
    
    # Build and run command
    cmd = [python_cmd, str(script_path)] + args
    
    # Execute and return the exit code
    result = subprocess.run(cmd, cwd=str(project_root))
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())