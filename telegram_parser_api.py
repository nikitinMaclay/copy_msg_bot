from colorama import Fore
# pip install PySocks, чтобы скачать socks
import socks
import time
import random
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty


# Создай глобальную переменную
# Ниже пример как я себе это представляю, в масиве содержится множество юзеров с уникальным API,
# делать запрос для конкретного модера, желательно с его собственного API
# users =
# [
#   {
#       'id':user_id,
#       'api':API(api_id, api_hash, phone, group_name)
#   }
# ]


# Ошибка на случай если группа не найдена
class GroupIsNotFound(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        return 'Группа не найдена!'


# если Проксей будет больше, то читай их в этот список
proxy_base = ['45.133.34.19:8000:GcDvZG:vkgyMg']


# просто слип со встроенным рандомом и принтом
def timeout(mn: int, mx: int):
    t = random.randrange(mn, mx)
    print(Fore.BLUE + f'Времени для продолжения работы {t}')
    time.sleep(t)


# При подключении:
# Текст Красный - Ошибка, почитай коменты, если там нет ответа на твой вопрос пиши мне
# Текст Белый - всё идет правильно
# Текст Зеленый - успешное поделючение
class API:
    def __init__(self, api_id: int, api_hash: str, phone: str):
        global proxy_base
        self.phone = phone
        self.logged = False
        proxy = (socks.SOCKS5, *random.choice(proxy_base).split(':'))
        self.client = TelegramClient(phone, api_id, api_hash, proxy=proxy)
        self.client.connect()
        print(Fore.WHITE + f'API по номеру {self.phone}. Подключен')
        if not self.client.is_user_authorized():
            print(Fore.WHITE + f'API по номеру {self.phone}. Нужно подтверждение кода - sign_in(code)')
            self.client.send_code_request(phone)
            print(Fore.WHITE + f'API по номеру {self.phone}. Код отправлен')
        else:
            self.logged = True
            print(Fore.WHITE + f'API по номеру {self.phone}. Логин уже пройден, код не нужен')
        self.target_group = None

    # Повторная отправка кода, в случае ошибки. Лучше вызывай по колбэку
    async def code_again(self):
        await self.client.send_code_request(self.phone)

    # После создания класса, в телегу на номер придут код, его передавай в переменную code
    # и вызови эту функцию, когда чел зарегается в боте
    async def login(self, code):
        if not self.client.is_user_authorized():
            try:
                await self.client.sign_in(self.phone, code)
                self.logged = True
                print(Fore.WHITE + f'API по номеру {self.phone}. Логин пройден, нужен запрос группы')
            except:
                print(Fore.RED + f'API по номеру {self.phone}. Подключение не удалось, нужен повторный запрос')
        else:
            print(Fore.WHITE + f'API по номеру {self.phone}. Логин уже пройден, код не нужен')

    # Попроси имя чата, и передай его в group_name, вызови после успешного логина
    async def get_chat(self, url: str):
        try:
            self.target_group = await self.client.get_entity(url)
            print(Fore.GREEN + f'API по номеру {self.phone}. Чат найден, API готов к работе')
            return 1
        except:
            print(Fore.RED + f'API по номеру {self.phone}. Чат не найден.')
            return 0

    # Это уже сам парсинг группы:
    # limit - количество последних сообщений, которые читаются
    # в них входят и не подходящие сообщения, поэтому пустой результат это не всегда плохо
    # .........................................................................................................
    # sec_min/sec_max - время ожидания между чтением сообщения (минимальное и максимальное значение в секундах)
    # .........................................................................................................
    # Возвращает тебе список сообщений type.Message, уже фильтрованных, тебе их нужно отправлять модеру
    async def parse(self, limit=5, sec_min=10, sec_max=20):
        if not self.logged:
            res = []
            iter_user_id = []
            with open('user_ids.txt', mode='r') as f:
                data = f.readlines()
            for k in range(len(data)):
                data[k] = int(data[k].replace('\n', ''))
            for message in self.client.iter_messages(self.target_group, limit=limit):
                timeout(sec_min, sec_max)
                if message.reply_to is None:
                    if '?' in message.text:
                        if message.sender_id not in data and str(message.sender_id) not in iter_user_id:
                            iter_user_id.append(str(message.sender_id))
                            res.append(message)
                            # этот принт сообщения можешь убрать, если
                            print(message)
            with open('user_ids.txt', mode='a') as f:
                f.writelines(iter_user_id)
            res.reverse()
            return res
        else:
            print(Fore.RED + f'API по номеру {self.phone}. Логин не пройден. Невозможно запустить парсинг')
            return None

# Если будут проблемы пиши, звони
# Я сидел до четырех, поэтому надеюсь, что всё будет работать хорошо


api = API(15187043, 'f882c210378bfcdf6b17fa3f8ce13433', '+77772566585')
await api.get_chat('code')
await api.parse()

