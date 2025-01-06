from package_c import main


def test_main():
    assert main() == "Hello from package_c!", (
        f"Expected 'Hello from package_c!', got main()"
    )