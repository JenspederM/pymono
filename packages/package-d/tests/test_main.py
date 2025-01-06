from package_d import main


def test_main():
    assert main() == "Hello from package_d!", (
        f"Expected 'Hello from package_d!', got main()"
    )