import pandas as pd
import geopandas as gpd
# TEST_DATE = datetime.datetime(2021, 11, 21, 1, 7, 43, 17500)
# eastern = pytz.timezone("US/Eastern")
# test_case = eastern.localize(TEST_DATE)
str_test_case = '2021-11-21 01:07:43.0175-05:00'
# numpy doesn't support timezones, so how does fiona/ geopandas work?
field_data = [
    # np.array([str_test_case, str_test_case], dtype="datetime64[ms]")
    pd.to_datetime([str_test_case, str_test_case])
]

df = gpd.GeoDataFrame({"col1": pd.to_datetime([str_test_case, str_test_case])},geometry=[None, None])

from pyogrio.geopandas import read_dataframe, write_dataframe
# print(df.dtypes)
# print(df['col1'].dt.type)
# write_dataframe(df, path="out.geojson", )
print("READING")
df = read_dataframe("out.geojson")
print(df)
