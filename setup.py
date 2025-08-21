"""
Setup script for LynxLogger library
"""

import os
import re
from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    with open(os.path.join("lynx_logger", "__init__.py"), "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Version not found")

def read_requirements():
    """Читает requirements из файла"""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

requirements = read_requirements()

setup(
    name="lynx-logger",
    version=get_version(),
    author="FlacSy",
    author_email="flacsy.x@gmail.com",
    description="Универсальная библиотека структурированного логирования на основе structlog",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NullPointerGang/lynx-logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Debuggers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "web": [
            "fastapi>=0.68.0",
            "flask>=2.0.0",
            "django>=3.2.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "fastapi>=0.68.0",
            "flask>=2.0.0",
            "django>=3.2.0",
        ]
    },
    keywords="logging, structlog, structured-logging, tracing, middleware",
    project_urls={
        "Bug Reports": "https://github.com/NullPointerGang/lynx-logger/issues",
        "Source": "https://github.com/NullPointerGang/lynx-logger"
    },
    include_package_data=True,
    zip_safe=False,
) 