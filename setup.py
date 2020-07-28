from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
    entry_points={
        "console_scripts": [
            "codeartifact-pip-login = codeartifact_release.login:main",
            "codeartifact-release = codeartifact_release.perform_release:main"
        ]
    }
)
