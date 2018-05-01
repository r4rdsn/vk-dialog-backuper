'''использование: vk-dialog-backuper [опции]

опции:
    -h --help                 вывести это сообщение и выйти
    -v --version              вывести версию программы и выйти
    -t --token TOKEN          авторизоваться через токен
    -l --login LOGIN          авторизоваться с использованием этого логина
    -p --password PASSWORD    авторизоваться с использованием этого пароля
    -f --file FILE            сохранить бэкап в архив с этим названием
    -d --directory DIRECTORY  сохранить бэкап в директорию с этим названием
    --leave-chats             выйти из всех бесед
    --delete-dialogs          удалить сохранённые диалоги
    --proxy URL               использовать указанный HTTP/HTTPS/SOCKS5 прокси
                              для использования SOCKS5 прокси, укажите протокол в адресе
                              например, socks5://127.0.0.1:1080/
'''

import sys
from getpass import getpass
from urllib.parse import urlparse

from .backuper import VkDialogBackuper
from .utils import docopt


__version__ = '1.0'
__author__ = 'alfred richardsn'
__description__ = 'утилита для бэкапа сообщений вк'


def start(args):
    kwargs = {}

    if args['--login'] and args['--password']:
        kwargs['login'] = args['--login']
        kwargs['password'] = args['--password']
    elif args['--token']:
        kwargs['token'] = args['--token']
    else:
        kwargs['login'] = input('Введите логин: ')
        kwargs['password'] = getpass('Введите пароль: ')

    if args['--proxy']:
        parsed = urlparse(args['--proxy'])
        if parsed.scheme == 'socks5':
            kwargs['proxies'] = {'http': args['--proxy'], 'https': args['--proxy']}
        else:
            kwargs['proxies'] = {'http': 'http://' + parsed.netloc, 'https': 'https://' + parsed.netloc}

    kwargs['file_name'] = args['--file']
    kwargs['directory'] = args['--directory']
    kwargs['leave_chats'] = args['--leave-chats']
    kwargs['delete_dialogs'] = args['--delete-dialogs']

    backuper = VkDialogBackuper(**kwargs)
    backuper.backup()


def main():
    args = docopt(
        __doc__.replace('использование', 'usage', 1).replace('опции', 'options', 2),
        help=False, version=__version__
    )

    if args['--help']:
        print(__doc__)
        sys.exit()

    try:
        start(args)
    except KeyboardInterrupt:
        print()
        sys.exit()
