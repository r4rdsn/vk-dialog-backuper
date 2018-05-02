import json
from datetime import datetime
import os.path
from zipfile import ZipFile
from vk_api import VkApi, VkTools, VkRequestsPool

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, **kwargs):
        return iterable

from .utils import ask_yes_or_no, logger


class VkDialogBackuper(VkApi):
    def __init__(self, *args, filename=None, directory=None, leave_chats=False, delete_dialogs=False, proxies=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.http.proxies = proxies

        if not self.token['access_token']:
            logger.info('Авторизация')
            self.auth()

        self.vk = self.get_api()
        self.tools = VkTools(self)

        logger.info('Получение информации о пользователе')
        with VkRequestsPool(self) as pool:
            user = pool.method('users.get')
            dialogs = pool.method('messages.getDialogs')

        self.leave_chats = leave_chats
        self.delete_dialogs = delete_dialogs

        self.user_id = user.result[0]['id']
        dialog_count = dialogs.result['count']

        logger.info('Получение диалогов')
        self.dialogs = []
        for dialog in tqdm(self.get_all_dialogs(), total=dialog_count, leave=False):
            self.dialogs.append(dialog)

        self.alias = {}

        if directory:
            self.output = 'dir'
            self.directory = directory
        else:
            self.output = 'zip'
            if not filename:
                filename = 'vk-dialog-backup-{}.zip'.format(datetime.now().strftime('%d-%m-%Y-%H-%M-%S'))
            elif os.path.splitext(filename)[1] != '.zip':
                filename += '.zip'
            logger.info('Открытие файла ' + filename)
            self.zipf = ZipFile(filename, 'w')

    def auth_handler(self):
        logger.info('Необходимо подтверждение авторизации')
        code = input('Введите код из личного сообщения от Администрации: ')
        remember = ask_yes_or_no('Запомнить этот аккаунт?')
        return code, remember

    def get_all_dialogs(self):
        return self.tools.get_all_iter('messages.getDialogs', 200)

    def get_all_messages(self, **kwargs):
        return self.tools.get_all_iter('messages.getHistory', 200, kwargs)

    def run(self):
        try:
            self._run()
        finally:
            self._write('alias.json', self._dumps(self.alias))
            if self.output == 'zip':
                self.zipf.close()

    def _run(self):
        for dialog in self.dialogs:
            preview = dialog['message']
            chat_id = preview.get('chat_id')
            if chat_id:
                peer_id = 2_000_000_000 + chat_id
                filename = 'chat_{}.json'.format(chat_id)
                logger.info('Обработка беседы {} ({})'.format(chat_id, preview['title']))
            else:
                peer_id = preview['user_id']
                filename = 'user_{}.json'.format(preview['user_id'])
                logger.info('Обработка диалога с пользователем {}'.format(preview['user_id']))

            if self.leave_chats:
                if chat_id and not (preview['action'] == 'chat_kick_user' and preview['action_mid'] == self.user_id):
                    self.vk.messages.remove_chat_user(chat_id=chat_id, user_id=self.user_id)
                    logger.info('Выход из беседы {}'.format(chat_id))

            total_messages = self.vk.messages.get_history(peer_id=peer_id)['count'] + 1
            logger.info('Сохранение {} сообщений'.format(total_messages))

            messages = []
            members = set()
            for message in tqdm(self.get_all_messages(peer_id=peer_id), total=total_messages, leave=False):
                messages.append(message)
                members.add(str(message['from_id']))

            users = self.vk.users.get(user_ids=','.join(members))
            names = {u['id']: u['first_name'] + ' ' + u['last_name'] for u in users}

            self._write(filename, self._dumps({'names': names, 'items': messages}))

            self.alias[filename] = preview['title'] if chat_id else names[preview['user_id']]

            if self.delete_dialogs:
                self.vk.messages.delete_dialog(peer_id=peer_id)

    def _dumps(self, obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    def _write(self, filename, content):
        logger.info('Сохранение файла ' + filename)

        if self.output == 'zip':
            with self.zipf.open(filename, 'w') as file:
                file.write(content.encode())

        elif self.output == 'dir':
            with open(os.path.join(self.directory, filename), 'w') as file:
                file.write(content)
