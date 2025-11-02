from _libparse import LibertyAst, LibertyParser
from .__version__ import __version__

def __LibertyAst__to_dict(self):
    result = {}
    result["id"] = self.id
    if len(self.args):
        result["args"] = self.args
    if self.value != "":
        result["value"] = self.value
    if len(self.children):
        result["children"] = [child.to_dict() for child in self.children]
    return result

LibertyAst.to_dict = __LibertyAst__to_dict
