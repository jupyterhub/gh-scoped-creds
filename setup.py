from setuptools import find_packages, setup

setup(
    name="gh-scoped-creds",
    version="2.2",
    url="https://github.com/yuvipanda/gh-scoped-creds",
    license="3-clause BSD",
    author="Yuvi Panda",
    author_email="yuvipanda@gmail.com",
    description="Temporary, well scoped credentials for pushing to GitHub",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    platforms="any",
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            # Backwards compatible script providing former (pre 2.0) name
            "github-app-user-auth = gh_scoped_creds:main",
            "gh-scoped-creds = gh_scoped_creds:main",
        ],
    },
)
