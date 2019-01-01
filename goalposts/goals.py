from abc import ABC


class Goal(ABC):
    def __init__(self, target, current):
        self.target = target
        self.current = current

    def check(self) -> bool:
        return self._check(self.target, self.current)

    def _check(self):
        raise NotImplementedError('Do not call the base Goal directly.')

    def report(self):
        return {
            'current': self.current,
            'target': self.target,
            'reached': self.check()
        }


class LessThanGoal(Goal):
    def _check(self, target, current):
        return current < target


class GreaterThanGoal(Goal):
    def _check(self, target, current):
        return current > target


class EqualGoal(Goal):
    def _check(self, target, current):
        return target == current