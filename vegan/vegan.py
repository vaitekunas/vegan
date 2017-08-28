"""Vegan is a simplistic spam filter."""

# Load all submodules
from vegan.base import Base

from vegan.log import Log


class Vegan(Base):
    """Vegan is the main class."""

    """Logging facility (function Log.log)."""
    _log = None

    """Model, loaded during initialization."""
    _main_model = None

    """Contains all the loaded models"""
    _models = {}

    """Contains all the loaded accounts"""
    _accounts = {}

    def __init__(self, model=None, log=None, data=None):
        """Initialize vegan."""
        # Initialize base
        Base.__init__(self, Log(log).log)

        if model is not None:
            try:
                self.load_model(model)
            except Exception as e:
                self._log("Could not load model %s" % model, err=True)
            self.main_model = model

    def add_account(self, account, host, port, user, spam_folder="spam", ssl=True):
        """Add an IMAP account to vegan."""
        pass

    def fetch(self, save_to="vegan.json"):
        """Fetch emails from an account and write them to a file."""
        pass

    def fetch_external(self, file, spam=0):
        """Fetch an external file."""
        pass

    def delete(save_file="vegan.json"):
        """Delete a save file."""
        pass

    def train(self, data="vegan.json", seed=2017, test=0.10, learner="", model_out="vegan"):
        """Train a spam classifier using a learner.

        Use either a built in vegan learner (Naive Bayes), or one of the classifiers
        from scikit.
        """
        pass

    def test(self, model="vegan"):
        """Evaluate model's accuraccy."""
        pass

    def compare(self, seed=2017, test=0.10, training_data=True, test_data=True):
        """Compare all the loaded models."""
        pass

    def load_model(self, model="vegan"):
        """Load a trained model."""
        pass

    def veganize(self, confidence=0.95, interval=60, live=None):
        """Fetch new emails and classify them."""
        pass
