from setuptools import setup, find_packages

VERSION = '1.0.9'
DESCRIPTION = "Support file for ece4078 practicals content"


setup(
    name="ece4078",
    version=VERSION,
    author="Tin Tran",
    author_email="tin.tran1@monash.edu",
    description=DESCRIPTION,
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'': ['install_nginx', 'nginx-meshcat-proxy.conf']},
    install_requires=[],
    include_package_data=True
)
