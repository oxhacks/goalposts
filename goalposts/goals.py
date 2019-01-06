"""Goals to use to compare values against targets."""

from abc import ABC


class Goal(ABC):
    """Base goal that should be used to define other goals."""
    def __init__(self, target, current):
        self.target = target
        self.current = current

    def check(self) -> bool:
        """Determine if a target is met.

        :returns bool: whether or not the target beats the given check.

        """
        return self._check(self.target, self.current)

    def _check(self, target, current):
        """Check the current value against the target.

        :param target: the target threshold
        :param value: the value to compare
        :returns: whether or not the target was met

        """
        raise NotImplementedError('Do not call the base Goal directly.')

    def report(self) -> dict:
        """A report of the input parameters and whether or not it meets the required target."""
        return {
            'current': self.current,
            'target': self.target,
            'reached': self.check()
        }


class LessThanGoal(Goal):
    """Determine if one value is less than another."""
    def _check(self, target, current):
        return current <= target


class GreaterThanGoal(Goal):
    """Determine if one value is greater than another."""
    def _check(self, target, current):
        return current >= target


class EqualGoal(Goal):
    """Determine if two values are equal."""
    def _check(self, target, current):
        return target == current
