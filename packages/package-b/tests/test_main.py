from package_b import main


def test_main():
    assert main() == "Hello from package_b!", (
        f"Expected 'Hello from package_b!', got main()"
    )