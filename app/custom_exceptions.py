######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
	pass

class WishlistException(Exception):
	""" Generic exception class from which more specific wishlist resource exceptions are derived """


class WishlistNotFoundException(WishlistException):
	""" Raised when a given wishlist resource cannot be found for a specific id """


class WishlistOperationNotPermittedException(WishlistException):
	""" Raised when an operation is deemed to be unacceptable """


class ItemException(Exception):
	""" Generic exception class from which more specific item resource exceptions are derived """


class ItemNotFoundException(ItemException):
	""" Raised when an item cannot be found for a given wishlist """