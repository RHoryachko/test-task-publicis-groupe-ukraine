"""
Pytest configuration and shared fixtures for Django project.
"""
import pytest


@pytest.fixture
def user(db, django_user_model):
    """Create and return a regular user."""
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def csv_valid_content():
    """Valid CSV content with required columns and dates (DD.MM.YY, day>12 to avoid US format)."""
    return b"""Advertis,Brand,Start,End,Format,Platforr,Impr
Company A,Brand X,04.01.21,10.01.21,banner,DV360,1000
Company B,Brand Y,15.01.21,20.01.21,banner,Facebook,2000"""


@pytest.fixture
def csv_empty_dates():
    """CSV where Start/End are empty (invalid table)."""
    return b"""Advertis,Brand,Start,End,Format,Platforr,Impr
Electrolux,Electrolux,,,Banner,facebook,8848433"""


@pytest.fixture
def csv_start_gt_end():
    """CSV with one row where Start > End (should be skipped). 30.01.21 > 13.01.21 (30 Jan > 13 Jan)."""
    return b"""Advertis,Brand,Start,End,Format,Platforr,Impr
A,B,30.01.21,13.01.21,banner,DV360,100
C,D,04.02.21,11.02.21,banner,DV360,200"""
