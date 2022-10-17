from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in due_diligence/__init__.py
from due_diligence import __version__ as version

setup(
	name="due_diligence",
	version=version,
	description="This application for send Quote Due Diligence to customer via email and again send to customer on Acceptance of quote.",
	author="Offshore Evolution Pvt Ltd",
	author_email="dipesh@offshoreevolution.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
