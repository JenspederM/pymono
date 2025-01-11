from uvmono import UvMono


def test_init():
    p = UvMono()
    assert p._root.exists()
    assert p._packages_root.exists()
    assert p._packages
    assert p._packages[0].exists()
