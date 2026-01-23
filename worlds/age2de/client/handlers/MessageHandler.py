
import os
from queue import Queue
import queue

from ...campaign import XsdatFile

type Age2Message = tuple[int, str]

class MessageHandler:
    _last_sent_message_id: int = 0
    _new_message_id: int = 0
    _unsent_message_queue: Queue[Age2Message]
    _sending_messages: list[Age2Message]
    
    def __init__(self):
        self._unsent_message_queue = Queue()
        self._sending_messages = []
    
    def add_message(self, msg: str):
        new_msg: Age2Message = (self._new_message_id, msg)
        self._unsent_message_queue.put(new_msg)
        self._new_message_id += 1
    
    def try_write_to_folder(self, user_folder: str):
        if self.is_message_sending():   #Prevents overwrite
            return
        self.__dequeue_to_sending_messages()
        num_to_send = len(self._sending_messages)
        if num_to_send > 0:
            try:
                with open(user_folder + "messages.xsdat", "wb") as fp:
                    XsdatFile.write_int(fp, num_to_send)
                    for msg in self._sending_messages:
                        XsdatFile.write_int(fp, msg[0])
                        XsdatFile.write_string(fp, msg[1])
            except Exception as ex:
                print(ex)
    
    def try_flush_from_folder(self, user_folder: str):
        try:
            if os.path.exists(user_folder + "messages.xsdat"):
                os.remove(user_folder + "messages.xsdat")
        except Exception as ex:
            print(ex)
    
    def is_message_waiting(self) -> bool:
        return not self._unsent_message_queue.empty()
    
    def is_message_sending(self) -> bool:
        return len(self._sending_messages) > 0
    
    def is_packet_up_to_date(self, packet_message_id) -> bool:
        if self._last_sent_message_id <= packet_message_id:
            return True
        return False
    
    def confirm_messages_recieved(self, packet_message_id):
        # Ensure last sent message id is strictly the same or larger than last received message packet.
        if self._last_sent_message_id < packet_message_id:
            self._last_sent_message_id = packet_message_id
        
        # Ensure new message ids are strictly the same or larger than last sent message.
        if self._new_message_id < self._last_sent_message_id:
            self._new_message_id = self._last_sent_message_id
        self._sending_messages.clear()
    
    def __dequeue_to_sending_messages(self):
        for msg in self._drain_queue():
            self._last_sent_message_id = msg[0]
            self._sending_messages.append(msg)

    def _drain_queue(self):
        while True:
            try:
                yield self._unsent_message_queue.get_nowait()
            except queue.Empty:  # On Python 2, use Queue.Empty
                break
