from setuptools import find_packages, setup
setup(
    name='cairlib',
    packages=find_packages(include=['cairlib']),
    version='0.1.0',
    description='CAIR library for creating a client',
    author='Lucrezia Grassi',
    license='MIT',
    install_requires=["numpy"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
)
