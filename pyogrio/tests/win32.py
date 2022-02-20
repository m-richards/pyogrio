"""Run pytest tests manually on Windows due to import errors
"""
import sys
from pathlib import Path
import platform
from tempfile import TemporaryDirectory
import os
print(f"win32 sys path: {sys.path}\n", os.getcwd())
print("environment vars\n", os.environ)

if __name__ == "__main__":
    sys.path.insert(0, "D:\\a\\pyogrio\\pyogrio\\pyogrio\\tests")

    data_dir = Path(__file__).parent.resolve() / "fixtures"

    if platform.system() == "Windows":

        naturalearth_lowres = data_dir / Path("naturalearth_lowres/naturalearth_lowres.shp")
        test_fgdb_vsi = f"/vsizip/{data_dir}/test_fgdb.gdb.zip"

        from pyogrio.tests.test_core import test_read_info

        try:
            test_read_info(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        from pyogrio.tests.test_raw_io import (
            test_read,
            test_read_no_geometry,
            test_read_columns,
            test_read_skip_features,
            test_read_max_features,
            test_read_where,
            test_read_where_invalid,
            test_write,
            test_write_gpkg,
            test_write_geojson,
        )

        try:
            test_read(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        try:
            test_read_no_geometry(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        try:
            test_read_columns(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        try:
            test_read_skip_features(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        try:
            test_read_max_features(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        try:
            test_read_where(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        try:  # ERROR 1: "invalid" not recognised as an available field.
            test_read_where_invalid(naturalearth_lowres)
        except Exception as ex:
            print(ex)

        with TemporaryDirectory() as tmpdir:
            try:
                test_write(tmpdir, naturalearth_lowres)
            except Exception as ex:
                print(ex)


        # Warning 1: A geometry of type MULTIPOLYGON is inserted into layer test of geometry type POLYGON,
        # which is not normally allowed by the GeoPackage specification, but the driver will however do it.
        # To create a conformant GeoPackage, if using ogr2ogr, the -nlt option can be used to override the
        # layer geometry type. This warning will no longer be emitted for this combination of
        # layer and feature geometry type.
        with TemporaryDirectory() as tmpdir:
            try:
                test_write_gpkg(tmpdir, naturalearth_lowres)
            except Exception as ex:
                print(ex)

        with TemporaryDirectory() as tmpdir:
            try:
                test_write_geojson(tmpdir, naturalearth_lowres)
            except Exception as ex:
                print(ex)

