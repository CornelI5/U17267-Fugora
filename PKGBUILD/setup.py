from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fugora",
    version="1.0.0",
    author="CornelI5",
    description="Framework for Universal Gravitational Observation & Research Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CornelI5/U17267-Fugora",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24",
        "pyyaml>=6.0",
        "requests>=2.31",
        "pygame>=2.5",
    ],
    entry_points={
        'console_scripts': [
            'fugora=fugora.main:main',
        ],
    },
)
