import setuptools
from quick_manage.cli.main import ENTRY_POINT

with open("README.md", "r", encoding="utf-8") as handle:
    long_description = handle.read()

with open("requirements.txt", "r", encoding="utf-8") as handle:
    install_requires = [x.strip() for x in handle.read().split("\n") if x.strip()]


setuptools.setup(
    name="quick-manage",
    version="0.1.0",
    author="Matthew Jarvis",
    author_email="mattj23@gmail.com",
    description="Quick and lightweight management tools for small IT infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mattj23/quick-manage",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            f"{ENTRY_POINT}=quick_manage.cli.main:main",
        ]
    }
)
