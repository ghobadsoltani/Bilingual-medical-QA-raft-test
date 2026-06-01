#!/usr/bin/env python3
"""
Setup script for efficient-llm-adaptation project.
Allows optional pip install -e . for easy imports.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="efficient-llm-adaptation",
    version="0.1.0",
    author="Your Name",
    description="A lightweight project demonstrating LoRA fine-tuning of language models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/efficient-llm-adaptation",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
)
