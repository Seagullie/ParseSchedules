from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ParseSchedules',
    version='1.0.0',
    author='Seagullie@GitHub',
    description='Extracts .json representations of schedules from .docx files',
    
    packages=find_packages(),
)