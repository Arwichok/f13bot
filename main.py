import random
import string
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.utils.executor import Executor, set_webhook
from aiogram.dispatcher.webhook import WebhookRequestHandler



TOKEN = '1461663675:AAEyLq7OaB1YGNnwsJhIbhJ9v4Pd3o9_vrQ'
W_HOST = 'https://input.cf'
W_PATH = '/webhook'
W_URL = W_HOST + W_PATH
WA_HOST = '0.0.0.0'
WA_PORT = 8000
M = 'm'
U = 'u'
forms = {}


def gen_id(size=3, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


bot = Bot(TOKEN)
dp = Dispatcher(bot)
routes = web.RouteTableDef()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@routes.get('/')
async def root(request):
    return web.Response(
        content_type='text/html',
        text="hello, this site for <a href='t.me/f13bot'>f13bot</a>")

@routes.get('/f{code}')
async def f(request):
    code = request.match_info['code']
    if code not in forms:
        return web.Response(text='wrong form')
    log.info(f'form {code}')
    return web.Response(
        content_type='text/html',
        text=f'''
<title>Fill form</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<form
    action='/a{code}'
    method='post'
    onSubmit='window.close();'
>
    <input type='text' name='text'/><br/>
    <input type='submit' value='Submit'/>
</form>
''')


@routes.post('/a{code}')
async def a(request):
    code = request.match_info['code']
    if code not in forms:
        return web.Response(text='code not found')
    data = await request.post()
    log.info(f'action {code}')
    out = await bot.edit_message_text(
        "Your data: " + data['text'],
        forms[code][U],
        forms[code][M])
    print(out)
    del forms[code]
    return web.HTTPFound('/')


@dp.message_handler(commands=['start'])
async def start_handler(msg):
    code = gen_id()
    log.info(f'start {code}')
    bot_msg = await msg.answer('Fill the form: input.cf/f'+code)
    forms[code] = {U:msg.from_user.id, M:bot_msg.message_id}

async def on_startup(dp):
    await bot.set_webhook(W_URL)


async def on_shutdown(dp):
    await bot.delete_webhook()


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    executor = set_webhook(
        dispatcher=dp,
        webhook_path=W_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        web_app=app
    )
    executor.run_app(host=WA_HOST, port=WA_PORT)



'''
    app = web.Application()
    app.router.add_route('*', W_PATH, WebhookRequestHandler, name='webhook_handler')
    app.add_routes(routes)
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)
    executor.run_app(app,
        host=WA_HOST,
        port=WA_PORT)
'''
