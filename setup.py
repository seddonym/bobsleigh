from distutils.core import setup
from setuptools import find_packages


setup(
    name='bobsleigh',
    version='0.1.3',
    url='http://github.com/seddonym/bobsleigh/',
    author='David Seddon',
    author_email='david@seddonym.me',
    description='Helps write less code when deploying Django installations.',
    packages=find_packages(),
    include_package_data=True,
)
