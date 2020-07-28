import argparse

import pytest

import codeartifact_release.perform_release as perform_release


def test_version_type_correct():
    arg_value = perform_release.version_type('1.0.0')
    assert arg_value == '1.0.0'


def test_version_type_incorrect():
    with pytest.raises(argparse.ArgumentTypeError):
        perform_release.version_type('1.0')


def test_version_compare_true_x():
    assert perform_release.version_compare('1.0.0', '2.0.0') is True


def test_version_compare_true_y():
    assert perform_release.version_compare('1.0.0', '1.1.0') is True


def test_version_compare_true_z():
    assert perform_release.version_compare('1.0.0', '1.0.1') is True


def test_version_compare_false_x():
    assert perform_release.version_compare('1.0.0', '0.1.1') is False


def test_version_compare_false_y():
    assert perform_release.version_compare('1.1.0', '1.0.2') is False


def test_version_compare_false_z():
    assert perform_release.version_compare('1.0.1', '1.0.0') is False


def test_version_compare_false_equal():
    assert perform_release.version_compare('1.0.0', '1.0.0') is False
