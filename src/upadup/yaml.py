import typing as t

import ruamel.yaml

# see: https://stackoverflow.com/a/45717104/2669818
# construct specialzed string types which add an `lc` slot to
# store the line and column numbers


class _StrWithLoc(ruamel.yaml.scalarstring.ScalarString):
    __slots__ = "lc"

    style = ""

    def __new__(cls, value):
        return ruamel.yaml.scalarstring.ScalarString.__new__(cls, value)


# define StrWithLoc as above at runtime, but specialize it for type checkers
if t.TYPE_CHECKING:

    class Loc(t.NamedTuple):
        line: int
        col: int

    class StrWithLoc(str):
        lc: Loc

else:
    StrWithLoc = _StrWithLoc


class PreservedScalarStringWithLoc(ruamel.yaml.scalarstring.PreservedScalarString):
    __slots__ = "lc"


class DoubleQuotedScalarStringWithLoc(
    ruamel.yaml.scalarstring.DoubleQuotedScalarString
):
    __slots__ = "lc"


class SingleQuotedScalarStringWithLoc(
    ruamel.yaml.scalarstring.SingleQuotedScalarString
):
    __slots__ = "lc"


class ConstructorWithStrLocs(ruamel.yaml.constructor.RoundTripConstructor):
    def construct_scalar(self, node):
        if not isinstance(node, ruamel.yaml.nodes.ScalarNode):
            raise ruamel.yaml.constructor.ConstructorError(
                None,
                None,
                "expected a scalar node, but found %s" % node.id,
                node.start_mark,
            )

        offset_col = 0
        if node.style == "|" and isinstance(node.value, str):
            ret_val = PreservedScalarStringWithLoc(node.value)
        elif bool(self._preserve_quotes) and isinstance(node.value, str):
            if node.style == "'":
                ret_val = SingleQuotedScalarStringWithLoc(node.value)
                offset_col = 1
            elif node.style == '"':
                ret_val = DoubleQuotedScalarStringWithLoc(node.value)
                offset_col = 1
            else:
                ret_val = StrWithLoc(node.value)
        else:
            ret_val = StrWithLoc(node.value)
        ret_val.lc = ruamel.yaml.comments.LineCol()
        ret_val.lc.line = node.start_mark.line
        ret_val.lc.col = node.start_mark.column + offset_col
        return ret_val


_yaml_impl = ruamel.yaml.YAML(typ="rt")
_yaml_impl.preserve_quotes = True
_yaml_impl.Constructor = ConstructorWithStrLocs


def load(*args, **kwargs):
    return _yaml_impl.load(*args, **kwargs)
