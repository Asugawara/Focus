from setuptools import setup


setup(
    name="focus",
    version="0.1.0",
    install_requires=["logzero"],
    packages=["focus"],
    entry_points={"console_scripts": ["focus = focus.focus:main"]},
)
