class ASTError(Exception):
    pass


class InvalidScenarioInputError(ASTError):

    def __init__(self, message):
        super().__init__(message)


class LaneFindingError(ASTError):

    def __init__(self, message):
        super().__init__(message)
