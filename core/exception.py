# Custom Exceptions 

class CASEError(Exception):
    """Raised when the an UnknownException occurs."""
    pass

class ProviderNotFound(Exception):
    """Raised when provider is nto found in the providers.json file."""
    pass


class ApiKeyNotFound(Exception):
    """Raised when the api key is not found in the .env file."""
    pass
