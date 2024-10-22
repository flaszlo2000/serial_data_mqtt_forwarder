from dataclasses import Field, dataclass
from typing import Any, Dict, Type, TypeVar, cast

from utils.exc import IncorrectFallbackTypeException

T = TypeVar("T", bound = Type[Any])

@dataclass
class FallbackFieldMixin:
    """
    Helper mixin that helps with dataclasses where we would need to use default_factory but it should also contain somekind of type converting logic.
    With this you can define a simple dataclass field that has it's init parameter set to False (in this way this won't overrite anything), and a fallback protected field with the same name that gets the data in whatever type it's available.

    The logic is the following: the non-protected field will be set from the protected. It will be casted based on the non-protected field's annotated type.

    If the protected field does not have a field with the very same name, only without the starting "_" sign, that protected field will be ignored and nothing will happen.

    For instance:

    @dataclass
    class Person(FallbackFieldMixin):
        age: int = field(init = False)
        _age: str = field(default_factory = input, repr = False)

        #birth_year won't be set and neither a public differing_birth_year will be created
        birth_year: int = field(init = False)
        _differing_birth_year: str = field(default_factory = input, repr = False)   
    """ 
    
    @property
    def type_lookup_table(self) -> Dict[Type[Any], Type[Any]]:
        return dict()

    def _try_to_convert(self, field_name: str, original_value: Any, type_to_convert: T) -> T:
        type_to_convert = cast(T, self.type_lookup_table.get(type_to_convert, type_to_convert))

        try:
            converted_value = type_to_convert(original_value)
        except ValueError:
            raise IncorrectFallbackTypeException(f"*{field_name}*'s value ({original_value}) is required to be convertable to: {type_to_convert}!")

        return converted_value

    def _getFallbackFields(self) -> Dict[str, Any]:
        "Searches the dataclass for correct fallback fields and returns the non-protected field name with the correctly converted value"
        result: Dict[str, Any] = dict()

        # a fallback field starts with one underscore (two is not permitted in dataclasses)
        for protected_field_name in filter(lambda key: key.startswith("_"), self.__dataclass_fields__):
            unprotected_field_name = protected_field_name[1:] # the fallback field's pair must have the same name only without the underscore

            # if there is no correctly named pair to the fallback field, then we ignore the current field
            if unprotected_field_name in self.__dataclass_fields__:
                unprotected_field: Field[Any] = self.__dataclass_fields__[unprotected_field_name]

                # the unprotected (or public) field must have it's init param set to False, with this accidental overwrites can be avoided
                if unprotected_field.init:
                    continue

                t: Type[Any] = cast(Type[Any], unprotected_field.type) # yolo
                original_value = self.__getattribute__(protected_field_name)

                if isinstance(original_value, str) and original_value == "":
                    raise IncorrectFallbackTypeException(f"*{unprotected_field_name}*'s value is missing!")

                result[unprotected_field_name] = self._try_to_convert(protected_field_name, original_value, t)

        return result

    def _setupFallbackFieldPairs(self) -> None:
        "Sets fields to the instance based on the given fields dict"
        for name, value in self._getFallbackFields().items():
            setattr(self, name, value)

    def __post_init__(self) -> None:
        self._setupFallbackFieldPairs()
