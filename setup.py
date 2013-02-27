from distutils.core import setup

with open("README.rst", "rt") as fp:
    DESCRIPTION = fp.read()

def run_setup():
    setup(name="depsolver", version="0.0.1",
          packages=["depsolver",
              "depsolver.solver",
              "depsolver.solver.tests",
              "depsolver.tests",
          ],
          license="BSD",
          author="David Cournapeau",
          author_email="cournape@gmail.com",
          url="http://github.com/enthought/depsolver",
          description="Depsolver is a library to deal with package dependencies.",
          long_description=DESCRIPTION,
    )

if __name__ == "__main__":
    run_setup()
