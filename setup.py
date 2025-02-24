from setuptools import setup, find_packages

with open("./requirements.txt", encoding="utf-8") as f:
    file_contents = f.read()
    requirements = file_contents.splitlines()

packages = find_packages()

print(packages)

setup(
    name="ParseSchedules",
    version="1.0.0",
    author="Seagullie@GitHub",
    description="Extracts .json representations of schedules from .docx files",
    packages=packages,
    install_requires=requirements,
)
