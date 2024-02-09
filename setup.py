from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

packages = find_packages()

print(packages)

setup(
    name='ParseSchedules',
    version='1.0.0',
    author='Seagullie@GitHub',
    description='Extracts .json representations of schedules from .docx files',
    
    packages= packages + ["ParseSchedules"],
    install_requires=requirements,
)