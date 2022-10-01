import setuptools
import os
lib_folder = os.path.dirname(os.path.realpath(__file__))

try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def load_requirements(fname):
    reqs = parse_requirements(fname)
    return [str(ir.req) for ir in reqs]


# with open(lib_folder + '/requirements.txt') as f:
#     install_requires = f.read().splitlines()
    
setuptools.setup(
    name='selenium_super',
    version='1.1.0',
    author='Eden Nahum',
    author_email='Edenik5@gmail.com',
    description='Selenium web driver with super abilities',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/edenik/selenium_super',
    project_urls = {
        "Bug Tracker": "https://github.com/edenik/selenium_super/issues"
    },
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    license='MIT',
    install_requires=load_requirements('requirements.txt'),
)