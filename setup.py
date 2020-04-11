from setuptools import setup, find_packages

install_requires=['bitarray']

tests_require = [
    'pytest',
]

setup(
    name='eightdad',
    version='0.0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    url='https://github.com/pushfoo/eightdad',
    license='To be determined',
    author='pushfoo',
    author_email='pushfoo@gmail.com',
    description='Chip-8 interpreter that might one day also have other tools'
)