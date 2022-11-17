from setuptools import find_packages, setup

install_requires = []

setup(name="nandemo", version="0.0.1", description="Nandemo DeepL", packages=["nandemo"], author="minaminao", entry_points={'console_scripts': ['nandemo = nandemo.__main__:main']}, install_requires=install_requires)
