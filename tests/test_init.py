"""Test module initialization"""
import forex_bot


def test_package_version():
    """Test that package has a version attribute"""
    assert hasattr(forex_bot, "__version__")
    assert forex_bot.__version__ == "0.1.0"
