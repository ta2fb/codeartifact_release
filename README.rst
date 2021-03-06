*****************************
codeartifact_release
*****************************

This package cuts releases to codeartifact for repos based on pyex_cc

This repo was created from the cookie cutter https://github.com/ta2fb/pyex_cc

.. readme-marker

Development
###########

1. Download and install Anaconda or Miniconda
2. Create a new conda environment and activate it

.. code-block:: bash

    conda create --name codeartifact_release python=3.8
    conda activate codeartifact_release

3. Install the code and development dependencies in the current conda environment

.. code-block:: bash

    pip install -e .[dev]

4. Build project

.. code-block:: bash

    tox

Build commands
**************

Lint code, run tests, and build project

.. code-block:: bash

    tox

Build project

.. code-block:: bash

    tox -e build

Check code coverage

.. code-block:: bash

    tox -e coverage

Build sphinx docs

.. code-block:: bash

    tox -e docs

Lint code

.. code-block:: bash

    tox -e lint

Lint code, run tests, build project, create docs, run code coverage

.. code-block:: bash

    tox -e release

Run tests

.. code-block:: bash

    tox -e run_tests

Cutting Releases with this Package
##################################

Requirements:

* aws cli
* aws credentials configured
* git
* tox, twine in Python environment
* environment variables
    * CODEARTIFACT_DOMAIN_OWNER=123456789123
    * CODEARTIFACT_DOMAIN=test
    * CODEARTIFACT_REPOSITORY=pypi

.. warning:: Make sure you have write permissions to the CodeArtifact repository before running this command!

.. code-block:: bash

    codeartifact-release --version x.y.z
    # if you have a repo with multiple packages, you can specify the directories to loop through them
    codeartifact-release --version x.y.z --package_dirs package1,package2
