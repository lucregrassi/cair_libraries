from setuptools import find_packages, setup
setup(
    name='cair_libraries',
    packages=find_packages(include=['cair_libraries']),
    version='0.1.0',
    description='CAIR libraries',
    author='Lucrezia Grassi',
    license='MIT',
    install_requires=["numpy"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
)
