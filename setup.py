import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()
    
setuptools.setup(
    name='selenium_super',
    version='1.0.9',
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
    packages=['selenium_super'],
    install_requires=install_requires,
)