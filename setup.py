from setuptools import setup, find_packages

setup(
    name='weather_rp5',
    version='1.0.1',
    packages=find_packages(),
    author='Jakob Müller',
    author_email='jakob.mueller1004@gmail.com',
    description='Functions for retrieving weather data from rp5.ru',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jakmuell/weather_rp5/',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
