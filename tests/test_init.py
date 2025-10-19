"""Test module initialization"""
import mpers_bot


def test_package_version():
    """Test that package has a version attribute"""
    assert hasattr(mpers_bot, "__version__")
    assert mpers_bot.__version__ == "0.1.0"
