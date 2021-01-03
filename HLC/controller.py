from HLC.path_finder import PathFinder


class Controller(PathFinder):
    def __init__(self, mapSize):
        super().__init__(mapSize)
        self.pucksPoss = {}
        self.robotsPoss = {}

