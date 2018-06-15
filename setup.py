import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pgBlockchain",
    version="0.0.9",
    author="Prashant Gupta",
    author_email="prashantgupta24@gmail.com",
    description="A small working example of a cryptocurrency",
    long_description=long_description,
    url="https://github.com/prashantgupta24/blockchain",
    packages=setuptools.find_packages(),
    include_package_data=True,
    keywords=['blockchain', 'cryptocurrency', 'python3'],
    python_requires='>=3',
    install_requires=[
        'requests>=2.18.4',
        'rsa>=3.4.2',
        'Flask>=1.0.2',
        'pip>=9.0.3',
        'setuptools>=28.8.0',
        'python-dotenv>=0.8.2'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
