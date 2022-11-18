class Fig2SketchWarning(Exception):
    def __init__(self, code):
        self.code = code
