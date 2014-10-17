from distutils.core import setup
from setuptools import find_packages


setup(
    name='bobsleigh',
    version='1.0.1',
    url='http://github.com/seddonym/bobsleigh/',
    author='David Seddon',
    author_email='david@seddonym.me',
    description='Helps write less code when configuring Django installations.',
    packages=find_packages(),
    include_package_data=True,
)
