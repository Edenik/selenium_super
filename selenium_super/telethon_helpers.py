from telethon.sync import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, CheckUsernameRequest, UpdateUsernameRequest
from telethon.tl.types import InputPeerChannel
from telethon.tl.types import DocumentAttributeVideo
from telethon import functions

class TelethonHelpers(TelegramClient):
    def __init__(self, api_id, api_hash, client_name, restrict_users=False) :
        self.client = self.get_client(api_id, api_hash, client_name, init=True)
        self.restrict_users = restrict_users
        
    def get_client(self, api_id, api_hash, client_name, init=False):
        if init == False and self.client:
            return self.client
        else:
            client = TelegramClient.__init__(client_name, api_id, api_hash)
            client.start()
            return client
    
    def get_chat_id(self, entity_name=None, entity_id=None):
        dialogs = self.client.get_dialogs()
        for dialog in dialogs:
            if (entity_name and dialog.name == entity_name) \
                or (entity_id and dialog.message.peer_id == entity_id):
                return dialog

        return None
    
    def create_group_if_not_exist(self, entity_name, group_about, messages, avatar=None):
        chat_id = self.get_chat_id(entity_name=entity_name)

        if not chat_id:
            chat_id = self.create_group(entity_name, group_about)
            if avatar: 
                upload_file_result = self.client.upload_file(file=avatar)
                try:
                    result = self.client(functions.channels.EditPhotoRequest(
                        channel=chat_id,
                        photo=upload_file_result
                    ))
                except Exception as e:
                    print(f'Error setting group avatar.\n{e}')
            
            for message in messages:
                if message.get('type') == 'message':
                    self.send_message(entity_name, message.get('message'))  
                else: 
                    self.send_file(entity_name, message.get('path'))
                            
    def send_message(self, entity_name, message):
        try:
            dialog = self.get_chat_id(entity_name=entity_name)
            
            if dialog:
                response = self.client.send_message(entity=dialog, message=message)
            else: 
                print(f'No chat found - {entity_name}')
        except Exception as e:
            print(f'Error while sending telegram message\n{e}')
  
    def send_file(self, entity_name, file, text=None):
        try:
            dialog = self.get_chat_id(entity_name=entity_name)
            if dialog:
                attributes = ()
                if '.mp4' in file:
                    attributes=(DocumentAttributeVideo(0, 0, 0),)
                response = self.client.send_file(entity=dialog, file=file, attributes=attributes, caption=text)
            else: 
                print(f'No chat found - {entity_name}')
        except Exception as e:
            print(f'Error while sending telegram message\n{e}')

    def create_group(self, group_name, group_about=None):
        createdPrivateChannel = self.client(CreateChannelRequest(group_name,group_about,megagroup=True))

        newChannelID = createdPrivateChannel.__dict__["chats"][0].__dict__["id"]
        newChannelAccessHash = createdPrivateChannel.__dict__["chats"][0].__dict__["access_hash"]
        desiredPublicUsername = "myUsernameForPublicChannel"
        checkUsernameResult = self.client(CheckUsernameRequest(InputPeerChannel(channel_id=newChannelID, access_hash=newChannelAccessHash), desiredPublicUsername))
        if(checkUsernameResult==True):
            publicChannel = self.client(UpdateUsernameRequest(InputPeerChannel(channel_id=newChannelID, access_hash=newChannelAccessHash), desiredPublicUsername))
        if self.restrict_users:
            try:
                self.client.edit_permissions(entity=group_name, view_messages=True, send_games=False, send_gifs=False, send_inline=False, send_media=False, send_messages=False, send_polls=False, send_stickers=False, change_info=False)
            except Exception as e:
                print(f'Error while trying to edit group permissions.\nError: {e}')
        return newChannelID