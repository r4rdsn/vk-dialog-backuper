from setuptools import setup, find_packages

from vk_dialog_backuper import __author__, __version__, __description__
from os.path import abspath, dirname, join

with open(join(abspath(dirname(__file__)), 'README.md')) as file:
    long_description = file.read()


setup(
    name='vk-dialog-backuper',
    version=__version__,
    description=__description__,
    long_description=long_description,
    url='https://github.com/r4rdsn/vk-dialog-backuper',
    author=__author__,
    author_email='rchrdsn@protonmail.ch',
    license='MIT',
    keywords='vk',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=['vk_api', 'requests', 'tqdm'],
    extras_require={'socks': ['PySocks']},
    python_requires='==3.6.*',
    entry_points={
        'console_scripts': [
            'vk-dialog-backuper=vk_dialog_backuper:main',
        ],
    }
)
