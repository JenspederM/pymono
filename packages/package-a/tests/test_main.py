from package_a import main


def test_main():
    assert main() == "Hello from package_a!", (
        f"Expected 'Hello from package_a!', got main()"
    )