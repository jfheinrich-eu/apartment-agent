"""
Tests for the ApartmentSearchRunner.

Verifies that the runner correctly orchestrates the search workflow
using the contract: adapter.search(profile) -> list[Apartment]
"""

from unittest.mock import MagicMock, patch

from wohnung_agent.adapters.demo_adapter import DemoAdapter
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.models import Apartment, SearchProfile
from wohnung_agent.notifier import Notifier
from wohnung_agent.runner import ApartmentSearchRunner


def test_runner_processes_demo_adapter_without_exception(tmp_path):
    """
    Verify that the runner can process the DemoAdapter
    without raising any exceptions.
    """
    # Setup
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg", "Lüneburg"],
    )
    database = ApartmentDatabase(str(tmp_path / "test.db"))
    adapters = [DemoAdapter()]
    filter_engine = FilterEngine(profile)
    notifier = MagicMock(spec=Notifier)
    notifier.send = MagicMock()

    runner = ApartmentSearchRunner(
        adapters=adapters,
        filter_engine=filter_engine,
        database=database,
        notifier=notifier,
    )

    # Execute - should not raise any exceptions
    runner.run_once()

    # Verify that notifier was potentially called (depending on matches)
    # In this case, the demo adapter has one matching apartment and one rejected
    database.close()


def test_runner_calls_adapter_search_with_profile():
    """
    Verify that the runner calls adapter.search(profile)
    with the correct SearchProfile.
    """
    # Setup
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["TestCity"],
    )

    mock_adapter = MagicMock()
    mock_adapter.search.return_value = []  # Return empty list
    mock_adapter.__class__.__name__ = "MockAdapter"

    filter_engine = FilterEngine(profile)
    database = MagicMock()
    notifier = MagicMock()

    runner = ApartmentSearchRunner(
        adapters=[mock_adapter],
        filter_engine=filter_engine,
        database=database,
        notifier=notifier,
    )

    # Execute
    runner.run_once()

    # Verify that adapter.search() was called with the profile
    mock_adapter.search.assert_called_once_with(profile)


def test_runner_skips_rejected_apartments():
    """
    Verify that the runner skips apartments marked as rejected
    by the filter engine.
    """
    # Setup
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["TestCity"],
    )

    # Create an apartment that will be rejected (too expensive)
    too_expensive_apartment = Apartment(
        source="test",
        external_id="1",
        title="Too Expensive",
        url="https://example.com/1",
        city="TestCity",
        warm_rent_eur=950,  # Exceeds max_warm_rent
        rooms=3,
        has_kitchen=True,
    )

    mock_adapter = MagicMock()
    mock_adapter.search.return_value = [too_expensive_apartment]
    mock_adapter.__class__.__name__ = "MockAdapter"

    filter_engine = FilterEngine(profile)
    database = MagicMock()
    notifier = MagicMock()

    runner = ApartmentSearchRunner(
        adapters=[mock_adapter],
        filter_engine=filter_engine,
        database=database,
        notifier=notifier,
    )

    # Execute
    runner.run_once()

    # Verify that database.save_match() was NOT called
    database.save_match.assert_not_called()
    # Verify that notifier.send() was NOT called
    notifier.send.assert_not_called()
