from pymono import PyMono


def test_init():
    p = PyMono()
    assert p._root.exists()
    assert p._packages_root.exists()
    assert p._packages
    assert p._packages[0].exists()
