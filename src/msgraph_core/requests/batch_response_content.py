from typing import Optional, Dict, Any, Type, TypeVar, Callable
from io import BytesIO
import base64

from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import ParseNode
from kiota_abstractions.serialization import ParseNodeFactory
from kiota_abstractions.serialization import ParseNodeFactoryRegistry
from kiota_abstractions.serialization import SerializationWriter

from .batch_response_item import BatchResponseItem

T = TypeVar('T', bound='Parsable')


class BatchResponseContent(Parsable):

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchResponseContent class.
        BatchResponseContent is a collection of BatchResponseItem items, each with a unique request ID.
        """
        self._responses: Optional[List['BatchResponseItem']] = []

    @property
    def responses(self) -> Optional[Dict[str, 'BatchResponseItem']]:
        """
        Get the responses in the collection
        :return: A dictionary of response IDs and their BatchResponseItem objects
        :rtype: Optional[Dict[str, BatchResponseItem]]
        """
        return None if self._responses is None else self._responses

    @responses.setter
    def responses(self, responses: Optional[Dict[str, 'BatchResponseItem']]) -> None:
        """
        Set the responses in the collection
        :param responses: The responses to set in the collection
        :type responses: Optional[Dict[str, BatchResponseItem]]
        """
        if isinstance(responses, dict):
            self._responses = {response.id: response for response in responses.values()}
        else:
            self._responses = responses

    def response(self, request_id: str) -> 'BatchResponseItem':
        """
        Get a response by its request ID from the collection
        :param request_id: The request ID of the response to get
        :type request_id: str
        :return: The response with the specified request ID as a BatchResponseItem
        :rtype: BatchResponseItem
        """
        if not self._responses or request_id not in self._responses:
            raise ValueError(f"No response found for id: {request_id}")
        return self._responses[request_id]

    def response_body(self, request_id: str, type: Type[T]) -> Optional[T]:
        """ 
        Get the body of a response by its request ID from the collection
        :param request_id: The request ID of the response to get
        :type request_id: str
        :param type: The type to deserialize the response body to
        :type type: Type[T]
        :return: The deserialized response body
        :rtype: Optional[T]
        """
        if not self._responses or request_id not in self._responses:
            raise ValueError(f"No response found for id: {request_id}")

        if not issubclass(type, Parsable):
            raise ValueError("Type passed must implement the Parsable interface")

        response = self._responses[request_id]
        content_type = response.content_type
        if not content_type:
            raise RuntimeError("Unable to get content-type header in response item")

        response_body = response.body or BytesIO()
        try:
            try:
                parse_node = ParseNodeFactoryRegistry().get_root_parse_node(
                    content_type, response_body
                )
            except Exception:
                response_body.seek(0)
                base64_decoded_body = BytesIO(base64.b64decode(response_body.read()))
                parse_node = ParseNodeFactoryRegistry().get_root_parse_node(
                    content_type, base64_decoded_body
                )
                response.body = base64_decoded_body
            return parse_node.get_object_value(type.create_from_discriminator_value)
            # tests this
        except Exception:
            raise ValueError(
                f"Unable to deserialize batch response for request Id: {request_id} to {type}"
            )

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        """ 
        Gets the deserialization information for this object.
        :return: The deserialization information for this object
        :rtype: Dict[str, Callable[[ParseNode], None]]
        """
        return {
            'responses':
            lambda n: setattr(
                self, "_responses", n.get_collection_of_object_values(BatchResponseItem.create)
            )
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Writes the objects properties to the current writer.
        :param writer: The writer to write to
        """
        writer.write_collection_of_object_values('responses', self._responses.values())

    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> 'BatchResponseContent':
        """
        Creates a new instance of the appropriate class based on discriminator value
        :param parse_node: The parse node to use to read the discriminator value and create the object
        :type parse_node: ParseNode
        :return: BatchResponseContent
        :rtype: BatchResponseContent
        """
        return BatchResponseContent()
