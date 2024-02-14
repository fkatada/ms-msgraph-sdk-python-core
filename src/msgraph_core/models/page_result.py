from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.parsable_factory import ParsableFactory
from kiota_abstractions.serialization.serialization_writer import SerializationWriter
from kiota_abstractions.serialization.parse_node import ParseNode
from kiota_serialization_json.json_parse_node import JsonParseNode
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from typing import Any, List, Optional


class PageResult(Parsable):

    def __init__(self):
        self._odata_next_link: Optional[str] = None
        self._value: Optional[List[Any]] = None

    @property
    def odata_next_link(self) -> Optional[str]:
        return self._odata_next_link

    @property
    def value(self) -> Optional[List[Any]]:
        return self._value

    @odata_next_link.setter
    def odata_next_link(self, next_link: Optional[str]) -> None:
        self._odata_next_link = next_link

    @value.setter
    def value(self, value: Optional[List[Any]]) -> None:
        self._value = value

    @staticmethod
    def create_from_discriminator_value(parse_node):
        return PageResult()

    def set_value(self, value: List[Any]):
        self.value = value

    def get_field_deserializers(self):
        return {
            '@odata.nextLink':
            lambda parse_node: setattr(self, 'odata_next_link', parse_node.get_str_value()),
            'value':
            lambda parse_node: self.set_value(parse_node.get_collection_of_primitive_values(str))
        }

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_str_value('@odata.nextLink', self.odata_next_link, self.value)
        writer.write_collection_of_object_values('key', 'value', list(self.value))
