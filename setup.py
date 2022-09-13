import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='selenium_super',
    version='1.0.3',
    author='Eden Nahum',
    author_email='Edenik5@gmail.com',
    description='Selenium web driver with super abilities',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/edenik/selenium_super',
    project_urls = {
        "Bug Tracker": "https://github.com/edenik/selenium_super/issues"
    },
    license='MIT',
    packages=['selenium_super'],
    install_requires=['selenium', 'requests', 'telethon'],
)