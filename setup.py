from setuptools import find_packages, setup

setup(
    name="github-app-user-auth",
    version="1.1",
    url="https://github.com/yuvipanda/github-app-user-auth",
    license="3-clause BSD",
    author="Yuvi Panda",
    author_email="yuvipanda@gmail.com",
    description="Collection of git-credential helpers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    platforms="any",
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "github-app-user-auth = github_app_user_auth.auth:main",
        ],
    },
)
