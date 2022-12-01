import setuptools

with open("README.md", "r", encoding="utf-8") as handle:
    long_description = handle.read()

with open("requirements.txt", "r", encoding="utf-8") as handle:
    install_requires = [x.strip() for x in handle.read().split("\n") if x.strip()]


setuptools.setup(
    name="quick-manage",
    version="0.1.0",
    author="Matthew Jarvis",
    author_email="mattj23@gmail.com",
    description="Quick SSH Management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mattj23/quick-ssh-management",
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
            "quick=quick_manage.main:main",
        ]
    }
)