from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="u17267-fugora",
    version="1.0.0",
    author="CornelI5",
    author_email="CornelI5@users.noreply.github.com",
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
    ],
    extras_require={
        "gui": [
            "pygame>=2.5",
            "PyOpenGL>=3.1.7",
            "PyOpenGL_accelerate>=3.1.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "fugora=fugora.main:main",
        ],
    },
)
