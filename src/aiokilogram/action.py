from __future__ import annotations

import abc
import inspect
import re
from enum import Enum
from typing import Any, ClassVar, Generic, Optional, Type, TypeVar, overload

import attr


_ACTION_FIELD_TV = TypeVar('_ACTION_FIELD_TV', bound='ActionField')


@attr.s(slots=True)
class ActionField(abc.ABC):
    _name: str = attr.ib(init=False)

    @abc.abstractmethod
    def get_pattern(self, value: Optional[Any] = None) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def serialize(self, value: Any) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, str_value: str) -> Any:
        raise NotImplementedError

    def __set_name__(self, owner: Type[CallbackAction], name: str) -> None:
        self._name = name

    @overload
    def __get__(self: _ACTION_FIELD_TV, instance: None, owner: Type[CallbackAction]) -> _ACTION_FIELD_TV: ...

    @overload
    def __get__(self, instance: Optional[CallbackAction], owner: Type[CallbackAction]) -> Any: ...

    def __get__(self, instance, owner):
        if instance is not None:
            return instance.data[self._name]

        return self


@attr.s(slots=True)
class StringActionField(ActionField):
    pattern: str = attr.ib(default='.*')

    def get_pattern(self, value: Optional[Any] = None) -> str:
        if value is not None:
            assert isinstance(value, str)
            return re.escape(value)
        return self.pattern

    def serialize(self, value: Any) -> str:
        assert isinstance(value, str)
        return value

    def deserialize(self, str_value: str) -> Any:
        return str_value


@attr.s(slots=True)
class IntegerActionField(ActionField):
    pattern: str = attr.ib(default=r'\d*')

    def get_pattern(self, value: Optional[Any] = None) -> str:
        if value is not None:
            assert isinstance(value, int)
            return re.escape(str(value))
        return self.pattern

    def serialize(self, value: Any) -> str:
        assert isinstance(value, int)
        return str(value)

    def deserialize(self, str_value: str) -> Any:
        return int(str_value)


_ENUM_ACTION_FIELD_TV = TypeVar('_ENUM_ACTION_FIELD_TV', bound=Enum)


@attr.s(slots=True)
class EnumActionField(ActionField, Generic[_ENUM_ACTION_FIELD_TV]):
    enum_cls: Type[_ENUM_ACTION_FIELD_TV] = attr.ib()

    def serialize_enum_value(self, value: _ENUM_ACTION_FIELD_TV) -> str:
        return value.name

    def get_pattern(self, value: Optional[Any] = None) -> str:
        if value is not None:
            assert isinstance(value, self.enum_cls)
            return re.escape(value.name)

        options_str = '|'.join([
            self.serialize_enum_value(value)
            for value in self.enum_cls
        ])
        return f'({options_str})'

    def serialize(self, value: Any) -> str:
        assert isinstance(value, self.enum_cls)
        return value.name

    def deserialize(self, str_value: str) -> _ENUM_ACTION_FIELD_TV:
        return self.enum_cls[str_value]


_ACTION_TV = TypeVar('_ACTION_TV', bound='CallbackAction')


class CallbackAction(abc.ABC):
    __slots__ = ('_data',)

    SEP: ClassVar[str] = '/'

    def __init__(self, **data: Any):
        action_props = self.get_action_props()
        for name, value in data.items():
            if name not in action_props:
                raise AttributeError(f'Invalid action field {name} for {type(self).__name__}')
        self._data: dict[str, Any] = data

    @classmethod
    def get_action_props(cls) -> dict[str, ActionField]:
        return {
            name: member
            for name, member in inspect.getmembers(cls)
            if isinstance(member, ActionField)
        }

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @classmethod
    def get_pattern(cls, **values: Any) -> str:
        assert isinstance(values, dict)
        sep_pattern = re.escape(cls.SEP)
        parts: list[str] = []
        for name, field in sorted(cls.get_action_props().items()):
            parts.append(field.get_pattern(value=values.get(name)))

        main_pattern = sep_pattern.join(parts)
        return f'^{main_pattern}$'

    def serialize(self) -> str:
        parts: list[str] = []
        for name, field in sorted(self.get_action_props().items()):
            parts.append(field.serialize(getattr(self, name)))

        return self.SEP.join(parts)

    @classmethod
    def deserialize(cls: Type[_ACTION_TV], str_value: str) -> _ACTION_TV:
        parts = str_value.split(cls.SEP)
        kwargs: dict[str, Any] = {}
        for (name, field), prop_str_value in zip(sorted(cls.get_action_props().items()), parts):
            kwargs[name] = field.deserialize(prop_str_value)

        return cls(**kwargs)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self._data == other._data

    @classmethod
    def when(cls, **values) -> ActionParameterization:
        return ActionParameterization(action_cls=cls, values=values)

    def clone(self: _ACTION_TV, **kwargs: Any) -> _ACTION_TV:
        return type(self)(**dict(self.data, **kwargs))


@attr.s
class ActionParameterization:
    action_cls: Type[CallbackAction] = attr.ib(kw_only=True)
    values: dict[str, Any] = attr.ib(kw_only=True)

    def get_pattern(self, **values) -> str:
        return self.action_cls.get_pattern(**self.values, **values)
