from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
    entry_points={
        "console_scripts": [
            "perform_release = codeartifact_release.perform_release:main"
        ]
    }
)
