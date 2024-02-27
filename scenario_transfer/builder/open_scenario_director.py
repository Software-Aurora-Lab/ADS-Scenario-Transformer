from scenario_transfer.builder import Builder


class OpenScenarioDirector:
    """
    Director for building messages.
    """

    def __init__(self):
        self.builders = {}

    def register_builder(self, builder_type: type, builder: Builder):
        """
        Register a builder.
        """
        self.builders[builder_type] = builder
