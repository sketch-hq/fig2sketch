class Fig2SketchWarning(Exception):
    def __init__(self, code: str):
        self.code = code
