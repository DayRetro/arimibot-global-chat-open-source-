import discord
from discord.ext import commands
from discord import Embed
from discord import Guild
from discord import Permissions
import asyncio

client = discord.Client(command_prefix='!', intents=discord.Intents.all())

capturar_por_servidor = {}
enviar_por_servidor = {}

CREADOR_BOT_ID = '270021746181144578'


async def eliminar_invitacion(codigo_invitacion, message):
    invitaciones = await message.guild.invites()

    for inv in invitaciones:
        if inv.code == codigo_invitacion:
            await inv.delete()
            await message.channel.send(
                f'La invitación {codigo_invitacion} ha sido eliminada.')
            return

    await message.channel.send(
        f'¡Buen intento baboso! No te dejaré enviar la invitación: {codigo_invitacion}.'
    )


@client.event
async def on_ready():
    print(f'Listo como {client.user}.')

    await client.change_presence(activity=discord.Streaming(
        name='Estado: beta', url='https://www.twitch.tv/dayretrotv'))


@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return

        canal_capturar = capturar_por_servidor.get(message.guild.id)

        if message.content.startswith('!definir_canal'):
            if message.author.guild_permissions.administrator == False:
                return

            canal_capturar = message.channel

            capturar_por_servidor[message.guild.id] = canal_capturar
            enviar_por_servidor[message.guild.id] = canal_capturar

            return await message.channel.send(
                f'Canal de captura y envío definido: {canal_capturar.mention}'
            )

        if message.content.startswith('!definir_envio'):
            channelName, serverId, _ = message.content.split()
            
            #nombre_canal = message.content.split(' ')[1]
            #id_servidor_envio = message.content.split(' ')[2]
            
            canal_enviar = discord.utils.get(
                client.get_guild(int(serverId)).channels,
                name=channelName
            )

            enviar_por_servidor[serverId] = canal_enviar
            mensaje = f'Canal de envío definido: {canal_enviar.mention if canal_enviar is not None else "NINGUNO"} en el servidor de ID {id_servidor_envio}.'
            return await message.channel.send(mensaje)

        if canal_capturar is not None and message.channel == canal_capturar:
            for servidor, canal_enviar in enviar_por_servidor.items():
                if servidor != message.guild.id and canal_enviar is not None:
                    if 'discord.gg/' in message.content or 'discordapp.com/invite/' in message.content:
                        codigo_invitacion = message.content.split(
                            'discord.gg/')[1].split()[0]
                        await eliminar_invitacion(codigo_invitacion, message)
                    elif '@everyone' in message.content or '@here' in message.content:
                        if message.author.id == int(CREADOR_BOT_ID):
                            mensaje = f'{message.author.name} dijo: {message.content}'
                            await canal_enviar.send(mensaje)
                            await message.delete()
                            await asyncio.sleep(1)
                    elif message.author != client.user:
                        mensaje = f'{message.author.name} dijo: {message.content}'
                        if f'<@{CREADOR_BOT_ID}>' in message.content or f'<@!{CREADOR_BOT_ID}>' in message.content:

                            await canal_capturar.send(
                                f'No puedes mencionar al creador del bot en este canal, {message.author.mention} 😠'
                            )

                            return await message.delete()

                        embed = discord.Embed(
                            title=f'{message.author.name} dijo:',
                            description=message.content,
                            color=0x00ff00)
                        embed.set_footer(
                            text=
                            f'Enviado desde el servidor: {message.guild.name}')
                        await canal_enviar.send(embed=embed)
                        await asyncio.sleep(1)

    except Exception as e:
        print(f'Se produjo un error: {e}')

        if message.content.startswith('!eliminar'):
            # obtener el código de la invitación a eliminar
            codigo = message.content.split()[1]

            # buscar la invitación en el servidor
            invitacion = await client.fetch_invite(codigo)

            # eliminar la invitación
            await invitacion.delete()

#pone tu token aqui
client.run('')
