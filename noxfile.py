import nox

# requires = [
#     "cython",
#     "numpy",
#     "geopandas"
# ]
# GDAL_INCLUDE_PATH = r"C:\OSGeo4W\include"
GDAL_INCLUDE_PATH = r"C:\gdal\include"
# GDAL_LIB_PATH = r"C:\OSGeo4W\lib"
GDAL_LIB_PATH = r"C:\gdal\lib"

from nox import Session


@nox.session(reuse_venv=True)
def tests(session: Session):
    session.install("wheel", "cython~=0.29", "numpy~=1.19", "pandas", "pytest", "pytest-cov", "setuptools")

    session.run("gdalinfo", "--version", external=True)

    # session.run(
    #     "pip",
    #     "install",
    #     "--install-option=build_ext",
    #     # f'--install-option="-I{GDAL_INCLUDE_PATH}"',
    #     '--install-option="-IC:\OSGeo4W\include"',
    #     '--install-option="-lgdal_i"',
    #     f'--install-option="-L{GDAL_LIB_PATH}"',
    #     '--no-deps',
    #     '--force-reinstall',
    #     '--no-use-pep517',
    #     '-e',
    #     '.',
    #     '-v',
    #     external=True
    # )
    session.run(
        "python",
        "setup.py",
        "build_ext",
        # f'--install-option="-I{GDAL_INCLUDE_PATH}"',
        '-IC:\OSGeo4W\include',
        '-lgdal_i',
        f'-L{GDAL_LIB_PATH}',
        '-v',
        external=True
    )


    session.run("pytest", "-v")

@nox.session()
def session2(session: Session):

    session.run("gdalinfo", "--version", external=True)
