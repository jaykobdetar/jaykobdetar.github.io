#!/usr/bin/env python3
"""
Project Cleanup Script
======================
Removes temporary files, caches, and maintains project cleanliness
"""

import os
import shutil
import sys
from pathlib import Path

def cleanup_project():
    """Clean up the project directory"""
    
    project_root = Path(__file__).parent.parent
    print(f"🧹 Cleaning up project: {project_root}")
    
    # Patterns to clean
    cleanup_patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo", 
        "**/*.tmp",
        "**/*.bak",
        "**/*~",
        "**/*.orig",
        "**/.*cache*",
        "**/.DS_Store",
        "**/Thumbs.db"
    ]
    
    # Directories to clean completely
    cleanup_dirs = [
        "scripts/logs",
        "src/**/__pycache__",
        "tests/**/__pycache__"
    ]
    
    # Files cleaned counter
    cleaned_count = 0
    
    print("\n📂 Cleaning cache files...")
    for pattern in cleanup_patterns:
        for path in project_root.glob(pattern):
            try:
                if path.is_file():
                    path.unlink()
                    print(f"  ✅ Removed file: {path.relative_to(project_root)}")
                    cleaned_count += 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    print(f"  ✅ Removed directory: {path.relative_to(project_root)}")
                    cleaned_count += 1
            except Exception as e:
                print(f"  ⚠️ Could not remove {path}: {e}")
    
    print("\n📁 Cleaning specific directories...")
    for dir_pattern in cleanup_dirs:
        for path in project_root.glob(dir_pattern):
            if path.is_dir():
                try:
                    shutil.rmtree(path)
                    print(f"  ✅ Removed: {path.relative_to(project_root)}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  ⚠️ Could not remove {path}: {e}")
    
    print("\n🔍 Checking for security issues...")
    
    # Check for potentially sensitive files
    sensitive_patterns = [
        "**/*.key",
        "**/*.pem", 
        "**/.env",
        "**/config.ini",
        "**/*password*",
        "**/*secret*"
    ]
    
    sensitive_found = []
    for pattern in sensitive_patterns:
        for path in project_root.glob(pattern):
            if path.is_file():
                sensitive_found.append(path)
    
    if sensitive_found:
        print("  ⚠️ Found potentially sensitive files:")
        for path in sensitive_found:
            print(f"    - {path.relative_to(project_root)}")
    else:
        print("  ✅ No sensitive files found")
    
    print("\n📊 Project Statistics:")
    
    # Count files by type
    file_counts = {}
    total_size = 0
    
    for path in project_root.rglob("*"):
        if path.is_file():
            suffix = path.suffix or "no extension"
            file_counts[suffix] = file_counts.get(suffix, 0) + 1
            try:
                total_size += path.stat().st_size
            except:
                pass
    
    print(f"  📁 Total files: {sum(file_counts.values())}")
    print(f"  💾 Total size: {total_size / 1024 / 1024:.1f} MB")
    print(f"  🧹 Files cleaned: {cleaned_count}")
    
    print("\n📋 File types:")
    for suffix, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {suffix:15}: {count:4d} files")
    
    print("\n✨ Cleanup completed!")
    
    return cleaned_count

def verify_security():
    """Verify security implementations are in place"""
    
    project_root = Path(__file__).parent.parent
    print(f"\n🔒 Verifying security implementations...")
    
    # Check for trusted security files
    security_files = [
        "src/utils/trusted_security.py",
        "src/utils/security_middleware.py",
        "assets/js/trusted-sanitizer.js",
        "requirements-security.txt",
        "SECURITY.md"
    ]
    
    missing_files = []
    for file_path in security_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Missing security files:")
        for file_path in missing_files:
            print(f"    - {file_path}")
        return False
    
    # Check for removed old security files
    old_files = [
        "src/utils/sanitizer.py",
        "src/utils/validators.py", 
        "src/utils/security_analyzer.py"
    ]
    
    found_old = []
    for file_path in old_files:
        full_path = project_root / file_path
        if full_path.exists():
            found_old.append(file_path)
    
    if found_old:
        print(f"  ⚠️ Old security files still present:")
        for file_path in found_old:
            print(f"    - {file_path}")
        return False
    
    print("  ✅ All security implementations verified")
    return True

if __name__ == "__main__":
    print("🧹 Project Cleanup & Security Verification")
    print("=" * 50)
    
    # Run cleanup
    cleaned_count = cleanup_project()
    
    # Verify security
    security_ok = verify_security()
    
    print("\n" + "=" * 50)
    if security_ok:
        print("✅ Project is clean and secure!")
    else:
        print("⚠️ Security issues detected - please review")
        sys.exit(1)
    
    print(f"🎉 Cleanup complete - {cleaned_count} items removed")