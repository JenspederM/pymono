"""Tests for the package_a package"""

from package_a import main


def test_main():
    """Test the main function"""
    expected = "Hello from package_a!"
    actual = main()
    assert actual == expected, f"Expected {expected}, got {actual}"


# def test_spark(spark):
#     assert spark is not None, "Spark session not created"
#     df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
#     assert df.count() == 2, "Dataframe not created"
#     df.write.format("delta").saveAsTable("test_table")
#     assert spark.table("test_table").count() == 2, "Table not created"
