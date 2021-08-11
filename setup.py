import setuptools


with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()


setuptools.setup(
    name="worldtools-xImAnton",
    version="0.1.1",
    author="xImAnton_",
    description="A python module for reading and writing Minecraft Worlds",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/xImAnton/WorldTools",
    project_urls={
        "Bug Tracker": "https://github.com/xImAnton/WorldTools/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8"
)