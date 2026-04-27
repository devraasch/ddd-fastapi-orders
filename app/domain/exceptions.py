class DomainError(Exception):
    pass


class InvalidOrderItemError(DomainError):
    pass


class OrderMutationNotAllowed(DomainError):
    pass
