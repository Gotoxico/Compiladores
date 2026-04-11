class TreeNode:
    def __init__(self, type=None, value=None):
        self.type = type
        self.value = value
        self.children = []
    
    def add_child(self, child):
        if child is not None:
            self.children.append(child)
        
    def set_type(self, type):
        self.type = type