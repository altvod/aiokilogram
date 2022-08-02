from enum import Enum

from aiokilogram.action import (
    CallbackAction, StringActionField, EnumActionField,
)


def test_action():
    class MyEnum(Enum):
        first = 'first'
        second = 'second'

    class MyAction(CallbackAction):
        some_str = StringActionField()
        enum_value = EnumActionField(enum_cls=MyEnum)

    assert isinstance(MyAction.some_str, StringActionField)
    assert isinstance(MyAction.enum_value, EnumActionField)

    my_action = MyAction(some_str='qwerty', enum_value=MyEnum.second)
    assert my_action.some_str == 'qwerty'
    assert my_action.enum_value == MyEnum.second

    assert MyAction.get_pattern() == r'^(first|second)/.*$'
    assert MyAction.get_pattern(some_str='thing') == r'^(first|second)/thing$'
    assert MyAction.get_pattern(enum_value=MyEnum.first) == r'^first/.*$'
    assert MyAction.get_pattern(some_str='thing', enum_value=MyEnum.first) == r'^first/thing$'

    assert my_action.serialize() == 'second/qwerty'

    assert MyAction.deserialize('second/qwerty') == my_action
    assert MyAction.deserialize('first/qwerty') != my_action
