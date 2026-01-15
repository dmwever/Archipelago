
from queue import Queue

from ...campaign import XsdatFile

type Age2Message = tuple[int, str]

class MessageHandler:
    last_sent_message_id: int = 0
    _user_folder: str
    _new_message_id: int = 0
    _unsent_messages: Queue[Age2Message]
    _sending_messages: list[Age2Message]
    
    def __init__(self):
        self._unsent_messages = Queue()
        self._sending_messages = list[Age2Message]
    
    def add_message(self, msg: str):
        new_msg: Age2Message = (self._new_message_id, msg)
        self._unsent_messages.put(new_msg)
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
    
    def is_message_waiting(self) -> bool:
        return not self._unsent_messages.empty()
    
    def is_message_sending(self) -> bool:
        return len(self._sending_messages) > 0
    
    def confirm_messages_recieved(self):
        self._sending_messages.clear()
    
    def __dequeue_to_sending_messages(self):
        sentinel = object()
        for msg in iter(self._unsent_messages.get, sentinel):
            self._last_sent_message = msg[0]
            self._sending_messages.append(msg)