#APIs
import discord
from discord import Option
from discord.ext import commands
from discord.ui import InputText, Modal
#libs
import random as r
#files
import secret
import alias as a

intents = discord.Intents.all()
client = commands.Bot(command_prefix='NBFU.', intents=intents)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name='Glory to NBFU!', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', twitch_name='NBFUA'))
    print('All systems online!')

@client.event
async def on_message(ctx):
    #moderating
    #delete promotion messages in a.market
    if ctx.channel.id == a.market and ctx.content.startswith(a.forbidden_word): await ctx.channel.purge(limit=1)
    #delete any chat messages in a.market
    if ctx.channel.id == a.market and not ctx.content.startswith('!р') and not ctx.author.id == a.xo: await ctx.channel.purge(limit=1)
    #delete messages from a.xo in channels other than a.market
    if ctx.author.id == a.xo and ctx.channel.id != a.market: await ctx.channel.purge(limit=1) 
    #with a 1.5% add a heart
    if ctx.channel.id == a.general:
        reactToMessage = r.randint(0,75)
        if reactToMessage == 38: await ctx.add_reaction(a.heart)
    #delete messages in a.galery which don't have attachments; heart them
    if ctx.channel.id == a.galery:
        if not ctx.attachments: await ctx.channel.purge(limit=1)
        else: await ctx.add_reaction(a.heart)
    #heart publications to a.info
    if ctx.channel.id == a.info: await ctx.add_reaction(a.heart)
    #add a check, a cross and create a thread to any message in a.threads
    if ctx.channel.id == a.threads:
        await ctx.add_reaction(a.check)
        await ctx.add_reaction(a.cross)
        await ctx.create_thread(name=f'[{ctx.author.name[:1].upper()}]: {ctx.content}', auto_archive_duration=1440)

    #commands
    message = str(ctx.content)
    #check if the message has an answer for a previously generated example
    with open('example.txt', 'r') as f:
        result = f.readlines()
    if result[0] != 'None':
        if result[0][:len(result[0])-1] in message and ctx.author.id != a.client:
            await ctx.add_reaction(a.check)
            with open('example.txt', 'w') as f:
                f.write('None')
        
    #flip a coin!
    if 'Попытаться' in message:
        flip = r.randint(1,2)
        if flip == 1: await ctx.add_reaction(a.check)
        else: await ctx.add_reaction(a.cross)
    #8ball mention
    if client.user.mentioned_in(ctx):
        with open('logs.txt', 'a') as f:
            responses = f.readlines()
            await ctx.reply(f'{r.choice(responses)}', mention_author = True)
    if ctx.author.id != a.client or client.user.mentioned_in(ctx):
        with open('logs.txt', 'a') as f:
            f.write(f'\n{message}')
    await client.process_commands(ctx)

#check the client's latency
@client.slash_command(name='пинг', description='Информация о соединения бота с сервером.')
async def ping(ctx): await ctx.respond(f'Понг! ({round(client.latency * 1000)}мс)', ephemeral=True)

#generate an example
@client.slash_command(name='пример', description='Генерация случайного примера.')
async def example(ctx,
операция: Option(str, required=False, choices=a.opchoices, default=f'{r.choice(a.opchoices)}'),
сложность: Option(int, required=False, default=r.randint(5, 15), min=1, max=99)):
    with open('example.txt', 'r') as f:
        check = f.readlines()
    global example
    if check[0] == 'None':
        if операция == '+':
            example = a.Example(f'{r.randint(-100*сложность, 100*сложность)}', f'{r.randint(-100*сложность, 100*сложность)}')
            example.result = int(example.num1) + int(example.num2)
        elif операция == '-':
            example = a.Example(f'{r.randint(-100*сложность, 100*сложность)}', f'{r.randint(-100*сложность, 100*сложность)}')
            example.result = int(example.num1) - int(example.num2)
        elif операция == '*':
            example = a.Example(f'{r.randint(-100*сложность, 100*сложность)}', f'{r.randint(-1*сложность, 1*сложность)}')
            example.result = int(example.num1) * int(example.num2)
        elif операция == '/':
            example = a.Example(f'{r.randint(-100*сложность, 100*сложность)}', f'{r.randint(-1*сложность, 1*сложность)}')
            example.result = example.num1
            example.num1 = int(example.num2) * int(example.result)
        elif операция == '^':
            example = a.Example(f'{r.randint(-5*сложность, 5*сложность)}', f'{2}')
            example.result = int(example.num1) ** int(example.num2)
        with open('example.txt', 'w') as f:
            f.write(f'{example.result}\n{example.num1}{операция}{example.num2}=')
            await ctx.respond(f'{example.num1}{операция}{example.num2}=...')
    else: await ctx.respond(f'Предыдущий пример \"{check[1]}...\" не был решён.')
    
#purge x amount of messages
@client.slash_command(name='purge', description='Удалить определённое кол-во сообщений.')
@commands.has_role(a.publisher)
async def yeet(ctx, количество: Option(int, required=True)):
    await ctx.channel.purge(limit=количество)
    await ctx.respond(f'{количество} сообщений успешно удалено!', ephemeral=True)

#send a message by the bot
@client.slash_command(name='send', description='Отправить сообщение от лица бота.')
@commands.has_role(a.publisher)
async def send(ctx, сообщение: Option(str, required=True)):
    await ctx.send(f'{сообщение}')
    await ctx.respond('Сообщение успешно отправлено!', ephemeral=True)

#make a publication in a.info
class Publication(Modal):
    def __init__(self) -> None:
        super().__init__(title='Меню создания публикаций')
        self.add_item(InputText(label='Имя публикации', placeholder='Введите имя публикации...', style=discord.InputTextStyle.short)) 
        self.add_item(InputText(label= 'Содержание публикации', placeholder='Тема публикации этой недели: ...\n\nДоп. информация: ...', style=discord.InputTextStyle.long))
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.children[0].value, description=self.children[1].value, color=0xff802d)
        await interaction.response.send_message(embeds=[embed])

@client.slash_command(name='publish', description=f'Опубликуйте что-нибудь!')
async def publish(ctx):
    modal = Publication()
    await ctx.interaction.response.send_modal(modal)

client.run(secret.secret)