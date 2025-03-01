from setuptools import setup, find_packages

setup(
    name="website-testing-framework",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'selenium>=4.15.0',
        'beautifulsoup4>=4.12.0',
        'PyYAML>=6.0.1',
        'jinja2>=3.1.0',
        'pytest>=7.4.0',
        'python-dotenv>=1.0.0',
        'webdriver-manager>=4.0.0',
        'requests>=2.31.0',
        'pillow>=10.0.0',
        'rich>=13.0.0',
        'typing-extensions>=4.8.0'
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="An intelligent automated website testing framework",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/automation-testing",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'webtest=src.main:main',
        ],
    },
)