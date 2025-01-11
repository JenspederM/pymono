from uvmono import uvmono


def test_init():
    p = uvmono()
    assert p._root.exists()
    assert p._packages_root.exists()
    assert p._packages
    assert p._packages[0].exists()
