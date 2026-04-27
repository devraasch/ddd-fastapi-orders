class DomainError(Exception):
    pass


class InvalidOrderItemError(DomainError):
    pass


class OrderMutationNotAllowed(DomainError):
    pass


class CannotConfirmOrderError(DomainError):
    pass


class CannotCancelOrderError(DomainError):
    pass
