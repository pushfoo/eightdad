from setuptools import setup, find_packages

install_requires=['bitarray']

tests_require = [
    'pytest',
]


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='eightdad',
    version='0.0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    url='https://github.com/pushfoo/eightdad',
    license='BSD-2-Clause',
    author='pushfoo',
    author_email='pushfoo@gmail.com',
    description='Chip-8 interpreter that might one day also have other tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Topic :: System :: Emulators"
    ],
    python_requires='>=3.6'
)
