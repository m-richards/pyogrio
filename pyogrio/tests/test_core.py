from numpy import array_equal, allclose
import pytest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


from pyogrio import (
    list_drivers,
    list_layers,
    read_bounds,
    read_info,
    set_gdal_config_options,
    get_gdal_config_option,
)




data_dir = Path(__file__).parent.resolve() / "fixtures"
@pytest.fixture(scope="session")
def naturalearth_lowres():
    return data_dir / Path("naturalearth_lowres/naturalearth_lowres.shp")


@pytest.fixture
def naturalearth_lowres_vsi(tmp_path, naturalearth_lowres):
    """Wrap naturalearth_lowres as a zip file for vsi tests"""

    path = tmp_path / f"{naturalearth_lowres.name}.zip"
    with ZipFile(path, mode="w", compression=ZIP_DEFLATED, compresslevel=5) as out:
        # out.write(naturalearth_lowres, naturalearth_lowres.name)
        for ext in ["dbf", "prj", "shp", "shx"]:
            filename = f"{naturalearth_lowres.stem}.{ext}"
            out.write(naturalearth_lowres.parent / filename, filename)

    return f"/vsizip/{path}/{naturalearth_lowres.name}"


@pytest.fixture(scope="session")
def test_fgdb_vsi():
    return f"/vsizip/{data_dir}/test_fgdb.gdb.zip"


def test_list_drivers():
    all_drivers = list_drivers()

    # verify that the core drivers are present
    for name in ("ESRI Shapefile", "GeoJSON", "GeoJSONSeq", "GPKG", "OpenFileGDB"):
        assert name in all_drivers

    assert all_drivers["ESRI Shapefile"] == "rw"
    assert all_drivers["OpenFileGDB"] == "r"

    drivers = list_drivers(read=True)
    expected = {k: v for k, v in all_drivers.items() if v.startswith("r")}
    assert len(drivers) == len(expected)

    drivers = list_drivers(write=True)
    expected = {k: v for k, v in all_drivers.items() if v.endswith("w")}
    assert len(drivers) == len(expected)

    drivers = list_drivers(read=True, write=True)
    expected = {
        k: v for k, v in all_drivers.items() if v.startswith("r") and v.endswith("w")
    }
    assert len(drivers) == len(expected)


def test_list_layers(naturalearth_lowres, naturalearth_lowres_vsi, test_fgdb_vsi):
    assert array_equal(
        list_layers(naturalearth_lowres), [["naturalearth_lowres", "Polygon"]]
    )

    assert array_equal(
        list_layers(naturalearth_lowres_vsi), [["naturalearth_lowres", "Polygon"]]
    )

    # Measured 3D is downgraded to 2.5D during read
    # Make sure this warning is raised
    with pytest.warns(
        UserWarning, match=r"Measured \(M\) geometry types are not supported"
    ):
        fgdb_layers = list_layers(test_fgdb_vsi)
        # GDAL >= 3.4.0 includes 'another_relationship' layer
        assert len(fgdb_layers) >= 7

        # Make sure that nonspatial layer has None for geometry
        assert array_equal(fgdb_layers[0], ["basetable_2", None])

        # Confirm that measured 3D is downgraded to 2.5D during read
        assert array_equal(fgdb_layers[3], ["test_lines", "2.5D MultiLineString"])
        assert array_equal(fgdb_layers[6], ["test_areas", "2.5D MultiPolygon"])


def test_read_bounds(naturalearth_lowres):
    fids, bounds = read_bounds(naturalearth_lowres)
    assert fids.shape == (177,)
    assert bounds.shape == (4, 177)

    assert fids[0] == 0
    # Fiji; wraps antimeridian
    assert allclose(bounds[:, 0], [-180.0, -18.28799, 180.0, -16.02088])


def test_read_bounds_max_features(naturalearth_lowres):
    bounds = read_bounds(naturalearth_lowres, max_features=2)[1]
    assert bounds.shape == (4, 2)


def test_read_bounds_skip_features(naturalearth_lowres):
    expected_bounds = read_bounds(naturalearth_lowres, max_features=11)[1][:, 10]
    fids, bounds = read_bounds(naturalearth_lowres, skip_features=10)
    assert bounds.shape == (4, 167)
    assert allclose(bounds[:, 0], expected_bounds)
    assert fids[0] == 10


def test_read_bounds_where_invalid(naturalearth_lowres):
    with pytest.raises(ValueError, match="Invalid SQL"):
        read_bounds(naturalearth_lowres, where="invalid")


def test_read_bounds_where(naturalearth_lowres):
    fids, bounds = read_bounds(naturalearth_lowres, where="iso_a3 = 'CAN'")
    assert fids.shape == (1,)
    assert bounds.shape == (4, 1)
    assert fids[0] == 3
    assert allclose(bounds[:, 0], [-140.99778, 41.675105, -52.648099, 83.23324])


@pytest.mark.parametrize("bbox", [(1,), (1, 2), (1, 2, 3)])
def test_read_bounds_bbox_invalid(naturalearth_lowres, bbox):
    with pytest.raises(ValueError, match="Invalid bbox"):
        read_bounds(naturalearth_lowres, bbox=bbox)


def test_read_bounds_bbox(naturalearth_lowres):
    # should return no features
    with pytest.warns(UserWarning, match="does not have any features to read"):
        fids, bounds = read_bounds(naturalearth_lowres, bbox=(0, 0, 0.00001, 0.00001))

    assert fids.shape == (0,)
    assert bounds.shape == (4, 0)

    fids, bounds = read_bounds(naturalearth_lowres, bbox=(-140, 20, -100, 40))

    assert fids.shape == (2,)
    assert array_equal(fids, [4, 27])  # USA, MEX

    assert bounds.shape == (4, 2)
    assert allclose(
        bounds.T,
        [
            [-171.791111, 18.916190, -66.964660, 71.357764],
            [-117.127760, 14.538829, -86.811982, 32.720830],
        ],
    )


def test_read_info(naturalearth_lowres):
    meta = read_info(naturalearth_lowres)

    assert meta["crs"] == "EPSG:4326"
    assert meta["geometry_type"] == "Polygon"
    assert meta["encoding"] == "UTF-8"
    assert meta["fields"].shape == (5,)
    assert meta["dtypes"].tolist() == ["int64", "object", "object", "object", "float64"]
    assert meta["features"] == 177


@pytest.mark.parametrize(
    "name,value,expected",
    [
        ("CPL_DEBUG", "ON", True),
        ("CPL_DEBUG", True, True),
        ("CPL_DEBUG", "OFF", False),
        ("CPL_DEBUG", False, False),
    ],
)
def test_set_config_options(name, value, expected):
    set_gdal_config_options({name: value})
    actual = get_gdal_config_option(name)
    assert actual == expected


def test_reset_config_options():
    set_gdal_config_options({"foo": "bar"})
    assert get_gdal_config_option("foo") == "bar"

    set_gdal_config_options({"foo": None})
    assert get_gdal_config_option("foo") is None
