import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pychaperone",
    version="0.0.1",
    author="Brandon Bertelsen",
    author_email="brandon@bertelsen.ca",
    description="For monitoring processes related to data science that are embarassingly parallel and prone to failure",
    long_description=long_description,
    install_requires = [
        'requests',
        'ray',
        'peewee',
        'psutil'
    ],
    long_description_content_type="text/markdown",
    url="https://github.com/1beb/pychaperone",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)