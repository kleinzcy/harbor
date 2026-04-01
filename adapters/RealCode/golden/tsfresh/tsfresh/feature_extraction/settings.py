"""
Settings and parameter definitions for feature extraction.
"""



class FCParameters:
    """Base class for feature calculation parameters."""

    def __init__(self):
        self.params = {}

    def __getitem__(self, key):
        return self.params.get(key)

    def __contains__(self, key):
        return key in self.params

    def get(self, key, default=None):
        return self.params.get(key, default)

    def keys(self):
        return self.params.keys()


class MinimalFCParameters(FCParameters):
    """Minimal set of feature calculation parameters."""

    def __init__(self):
        super().__init__()
        self.params = {
            "mean": None,
            "variance": None,
            "length": None,
        }


class ComprehensiveFCParameters(FCParameters):
    """Comprehensive set of feature calculation parameters."""

    def __init__(self):
        super().__init__()
        # For now, same as minimal
        self.params = {
            "mean": None,
            "variance": None,
            "length": None,
            "time_stretch": None,
        }