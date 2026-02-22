"""
State management utilities.

Provides a React-like useState pattern for managing application state.
"""

import logging
from typing import Any, Callable, Tuple, TypeVar, Generic

logger = logging.getLogger(__name__)

T = TypeVar("T")


class UseState(Generic[T]):
    """
    A class to store and manage application state.

    This class mimics the useState hook pattern from React, providing
    a getter and setter for state management.

    Example:
        state, set_state = UseState("initial_value").init()
        set_state("new_value")
        print(state)  # Prints: new_value
    """

    def __init__(self, initial_value: T):
        """
        Initialize state with an initial value.

        Args:
            initial_value: The initial state value
        """
        self._value: T = initial_value

    def init(self) -> Tuple["UseState[T]", Callable[[T], None]]:
        """
        Initialize and return the state object and setter function.

        Returns:
            Tuple of (state_object, setter_function)
        """
        return self, self.set_value

    @property
    def value(self) -> T:
        """Get the current state value."""
        return self._value

    def set_value(self, new_value: T) -> None:
        """
        Set a new state value.

        Args:
            new_value: The new value to set
        """
        old_value = self._value
        self._value = new_value
        logger.debug(f"State changed: {old_value} -> {new_value}")

    def __repr__(self) -> str:
        """String representation returns the current value."""
        return str(self._value)

    def __eq__(self, other: Any) -> bool:
        """
        Compare state value with another value.

        Supports comparison with both UseState objects and raw values.
        """
        if isinstance(other, UseState):
            return self._value == other._value
        return self._value == other

    def __hash__(self) -> int:
        """Make UseState hashable based on its value."""
        return hash(self._value)


class StateManager:
    """
    Centralized state manager for application-wide state.

    Provides a registry for named states that can be accessed globally.
    """

    _states: dict = {}

    @classmethod
    def register(cls, name: str, initial_value: Any) -> Tuple[UseState, Callable]:
        """
        Register a new named state.

        Args:
            name: Unique name for the state
            initial_value: Initial value for the state

        Returns:
            Tuple of (state_object, setter_function)
        """
        state = UseState(initial_value)
        cls._states[name] = state
        logger.debug(f"Registered state: {name} = {initial_value}")
        return state.init()

    @classmethod
    def get(cls, name: str) -> UseState:
        """
        Get a registered state by name.

        Args:
            name: Name of the state to retrieve

        Returns:
            The UseState object

        Raises:
            KeyError: If state is not registered
        """
        if name not in cls._states:
            raise KeyError(f"State '{name}' is not registered")
        return cls._states[name]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered states."""
        cls._states.clear()
        logger.debug("All states cleared")
