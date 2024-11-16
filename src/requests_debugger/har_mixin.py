import dataclasses
import logging
import types

logger = logging.getLogger("requests_debugger")

_ATOMIC_TYPES = frozenset(
    {
        # Common JSON Serializable types
        types.NoneType,
        bool,
        int,
        float,
        str,
    }
)


def snake_to_camel(input: str) -> str:
    camel_cased = "".join(x.capitalize() for x in input.lower().split("_"))
    if camel_cased:
        return camel_cased[0].lower() + camel_cased[1:]
    else:
        return camel_cased


def fix_field_name(f: dataclasses.Field) -> str:
    if f.metadata.get("field_name"):
        return f.metadata["field_name"]
    else:
        return snake_to_camel(f.name)


class HarMixin:
    def to_dict(self, include_null=False) -> dict:
        """Converts this to json. Assumes variables are snake cased"""

        def convert(obj):
            logger.debug(f"START - Converting {obj.__class__} to dict")
            result = {}
            if type(obj) in _ATOMIC_TYPES:
                return obj
            elif isinstance(obj, (list, tuple)):
                return [convert(item) for item in obj]
            elif isinstance(obj, dict):
                return {snake_to_camel(k): convert(v) for k, v in obj.items()}
            elif hasattr(obj, "__dataclass_fields__"):
                for f in dataclasses.fields(obj):
                    fobj = getattr(obj, f.name)
                    logger.debug(
                        f"Field: {f.name=} {f.type=} {type(f.type)=} {f.metadata=} {fobj=} {type(fobj)=}"
                    )
                    result[fix_field_name(f)] = convert(getattr(obj, f.name))
            else:
                raise ValueError(f"Unsupported type {type(obj)}")

            logger.debug(f"END - Converting {obj.__class__} to dict")

            return result

        return convert(self)

    @property
    def is_valid(self):
        return self.validate()

    def validate(self):
        raise NotImplementedError("validate method must be implemented in subclass")
