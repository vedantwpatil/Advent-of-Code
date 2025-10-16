from node import Node


class BinarySearchTree:
    def __init__(self) -> None:
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = Node(value)
        self.insertRecursive(node=self.root, value=value)

    def insertRecursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value=value)
            else:
                self.insertRecursive(node=node.left, value=value)

        elif value > node.value:
            if node.right is None:
                node.right = Node(value=value)
            else:
                self.insertRecursive(node=node.right, value=value)

    def search(self, value):
        return self.searchRecursive(self.root, value)

    def searchRecursive(self, node, target):
        if node.value == target or node is None:
            return node

        if node.value < target:
            return self.searchRecursive(node.left, target)

        return self.searchRecursive(node.right, target)

    def treeToList(self):
        result = []
        self.treeToListRecursive(self.root, result)
        return result

    def treeToListRecursive(self, node, result):
        if node:
            self.treeToListRecursive(node.left, result)
            result.append(node.value)
            self.treeToListRecursive(node.right, result)
