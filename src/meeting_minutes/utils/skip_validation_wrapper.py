class SkipValidationWrapper:
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def __setattr__(self, name, value):
        if name == "_obj":
            super().__setattr__(name, value)
        else:
            setattr(self._obj, name, value)

    # Added to avoid AttributeError if underlying LLM lacks supports_stop_words.
    def supports_stop_words(self):
        if hasattr(self._obj, "supports_stop_words"):
            return self._obj.supports_stop_words()
        return False
