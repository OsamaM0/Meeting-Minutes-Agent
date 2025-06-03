"""Setup configuration for Meeting Minutes Agent."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="meeting-minutes-agent",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered meeting minutes generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/meeting-minutes-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pre-commit>=3.6.0",
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=7.0.0",
            "pytest>=7.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "meeting-minutes=meeting_minutes.main:main",
        ],
    },
)
