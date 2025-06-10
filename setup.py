#!/usr/bin/env python3
"""
Setup script for Influencer News CMS
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="influencer-news-cms",
    version="1.0.0",
    author="InfNews Contributors",
    author_email="contact@infnews.com",
    description="A comprehensive desktop content management system for static news websites focused on the influencer and creator economy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/InfNews",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/InfNews/issues",
        "Documentation": "https://github.com/yourusername/InfNews/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/InfNews",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Office/Business :: News/Diary",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses Python built-ins only
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "infnews=integration_manager:main",
            "infnews-sync=sync_site:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.md", "*.txt"],
    },
    keywords=[
        "cms",
        "content-management",
        "static-site",
        "news",
        "influencer",
        "creator-economy",
        "html-generator",
        "desktop-app",
        "gui",
        "python",
        "tkinter",
        "website-builder",
    ],
    zip_safe=False,
)