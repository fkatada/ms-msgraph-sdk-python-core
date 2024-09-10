from typing import List, Optional

from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import SerializationWriter

from .batch_request_content import BatchRequestContent
from .batch_request_item import BatchRequestItem


class BatchRequestContentCollection:
    """A collection of request content objects."""

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchRequestContentCollection class.
        Args:
            number of requests in a batch. Defaults to 20.
        
        """
        self.batches: List[BatchRequestContent] = []
        self.current_batch: BatchRequestContent = BatchRequestContent()

    def add_batch_request_item(self, request: BatchRequestItem) -> None:
        """ 
        Adds a request item to the collection.
        Args:
            request (BatchRequestItem): The request item to add.
        """
        try:
            self.current_batch.add_request(request)
        except ValueError as e:
            if "Maximum number of requests is" in str(e):
                self.batches.append(self.current_batch.finalize())

                self.current_batch = BatchRequestContent()
                self.current_batch.add_request(request)
        self.batches.append(self.current_batch)

    def remove_batch_request_item(self, request_id: str) -> None:
        """ 
        Removes a request item from the collection.
        Args:
            request_id (str): The ID of the request item to remove.
        """
        for batch in self.batches:
            for request in batch.requests:
                if request.id == request_id:
                    batch.requests.remove(request)
                    return
        for request in self.current_batch.requests:
            if request.id == request_id:
                self.current_batch.requests.remove(request)
                return

    def new_batch_with_failed_requests(self) -> Optional[BatchRequestContent]:
        """
        Creates a new batch with failed requests.
        Returns:
            Optional[BatchRequestContent]: A new batch with failed requests.
        """
        # Use IDs to get response status codes, generate new batch with failed requests
        batch_with_failed_responses: Optional[BatchRequestContent] = BatchRequestContent()
        for batch in self.batches:
            for request in batch.requests:
                if request.status_code not in [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]:
                    if batch_with_failed_responses is not None:
                        batch_with_failed_responses.add_request(request)
                    else:
                        raise ValueError("batch_with_failed_responses is None")
        return batch_with_failed_responses

    def get_batch_requests_for_execution(self) -> List[BatchRequestContent]:
        """
        Gets the batch requests for execution.
        Returns:
            List[BatchRequestContent]: The batch requests for execution.
        """
        # if not self.current_batch.is_finalized:
        #     self.current_batch.finalize()
        #     self.batches.append(self.current_batch)
        return self.batches

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        pass
        # print(f"serializing {self.batches}")
        # writer.write_collection_of_object_values("requests", self.batches)
