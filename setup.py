import setuptools
from llmpipeline import __version__

def parse_requirements(filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    requires = []

    for line in lines:
        if "http" in line:
            pkg_name_without_url = line.split('@')[0].strip()
            requires.append(pkg_name_without_url)
        else:
            requires.append(line)

    return requires

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="llmpipeline",  # Replace with your own username
    version=__version__,
    author="linluhe",
    author_email="is4test@163.com",
    description="LLMPipeline is a Python package designed to optimize the performance of tasks related to Large Language Models (LLMs)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/new-soul-house/LLMPipeline",
    packages=setuptools.find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    zip_safe=False,
)
