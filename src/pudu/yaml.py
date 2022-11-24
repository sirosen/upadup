import ruamel.yaml

# see: https://stackoverflow.com/a/45717104/2669818
# construct specialzed string types which add an `lc` slot to
# store the line and column numbers


class StrWithLoc(ruamel.yaml.scalarstring.ScalarString):
    __slots__ = "lc"

    style = ""

    def __new__(cls, value):
        return ruamel.yaml.scalarstring.ScalarString.__new__(cls, value)


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

        if node.style == "|" and isinstance(node.value, ruamel.yaml.compat.text_type):
            ret_val = PreservedScalarStringWithLoc(node.value)
        elif bool(self._preserve_quotes) and isinstance(
            node.value, ruamel.yaml.compat.text_type
        ):
            if node.style == "'":
                ret_val = SingleQuotedScalarStringWithLoc(node.value)
            elif node.style == '"':
                ret_val = DoubleQuotedScalarStringWithLoc(node.value)
            else:
                ret_val = StrWithLoc(node.value)
        else:
            ret_val = StrWithLoc(node.value)
        ret_val.lc = ruamel.yaml.comments.LineCol()
        ret_val.lc.line = node.start_mark.line
        ret_val.lc.col = node.start_mark.column
        return ret_val


_yaml_impl = ruamel.yaml.YAML(typ="rt")
_yaml_impl.Constructor = ConstructorWithStrLocs


def load(*args, **kwargs):
    return _yaml_impl.load(*args, **kwargs)
