import setuptools

ENTRY_POINT = "quick"

with open("README.md", "r", encoding="utf-8") as handle:
    long_description = handle.read()

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
    install_requires=[
        "cryptography~=38.0.4",
        "urllib3~=1.26.13",
        "paramiko~=2.12.0",
        "invoke~=1.7.3",
        "setuptools~=60.2.0",
        "fabric~=2.7.1",
        "minio~=7.1.12",
        "click~=8.1.3",
        "pytest~=7.2.0",
        "dacite~=1.6.0",
        "ruamel.yaml~=0.17.21",
    ],
    entry_points={
        "console_scripts": [
            f"{ENTRY_POINT}=quick_manage.cli.main:main",
        ]
    }
)
