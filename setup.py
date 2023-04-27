from setuptools import setup, find_packages

install_requires=[
    'bitarray==2.4.1',
    'arcade==3.0.0dev20',
    'asciimatics==1.14.0'
]


tests_require = [
    'pytest',
]


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='eightdad',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            'eightdad=eightdad.frontend.gl:main',
            'eightdad-tui=eightdad.frontend.tui:main'
        ]
    },
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Topic :: System :: Emulators"
    ],
    python_requires='>=3.8'
)
