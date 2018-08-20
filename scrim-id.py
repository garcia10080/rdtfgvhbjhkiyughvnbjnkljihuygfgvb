import discord
from discord.ext import commands

import asyncio
import traceback

import os


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('!'))
        self.checking_ids = False
        self.games = {}
        self.msg = None
        self.add_command(self.scrim)
        self.add_command(self.stop)

    def role(role_id):
        def wrapper(ctx):
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if ctx.author.top_role >= role:
                return True
            return False
        return commands.check(wrapper)

    @classmethod
    def run_bot(bot):
        bot = bot()
        try:
            bot.run(os.environ.get('token'))
        except Exception as e:
            print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))

    async def on_ready(self):
        print('Bot Online!')

    async def on_message(self, msg):
        if msg.author.bot:
            return

        if msg.channel.id == 478339552814301185 and self.checking_ids:
            if msg.content == '!stop':
                return await self.process_commands(msg)
            if len(msg.content) != 3:
                await msg.delete()
                return await msg.channel.send('{}, su mensaje debe tener 3 dígitos de largo!'.format(msg.author.mention), delete_after=3)
            if not self.games.get(msg.content.lower()):
                self.games[msg.content.lower()] = [msg.author.id]
            else:
                if msg.author.id in self.games[msg.content.lower()]:
                    return await msg.delete()
                self.games[msg.content.lower()].append(msg.author.id)
            await msg.delete()
            await self.update_embed()

        await self.process_commands(msg)

    async def update_embed(self):
        """Updates the embed"""
        em = discord.Embed(title='Servidores Actuales', color=discord.Color.blue())
        for i in self.games.keys():
            fmt = '\n'.join([self.get_user(m).mention for m in self.games[i]])
            fmt += '\n({} jugadores en total)'.format(len(self.games[i]))
            em.add_field(name=i, value=fmt, inline=True)
        if self.msg:
            await self.msg.edit(content='', embed=em)
        else:
            self.msg = await self.get_channel(478339552814301185).send(embed=em)

    @commands.command()
    @role(476854273892941824)
    async def scrim(self, ctx):
        """Empieza el scrim"""
        self.games = {}
        self.msg = None
        em = discord.Embed(
            title='Empienza la partida',
            description='Presione listo cuando la cuenta regresiva llegue a cero.',
            color=discord.Color.green()
        )

        await self.get_channel(478339552814301185).send(embed=em)
        await self.get_channel(478339552814301185).send('Escribe los ultimos 3 digitos de tu partida.')
        self.checking_ids = True
        await asyncio.sleep(120)
        if not self.checking_ids:  # used stop command
            return
        self.checking_ids = False
        print('Checking stopped!')
        await self.get_channel(478339552814301185).send('El tiempo ha terminado!')

    @commands.command()
    @role(476854273892941824)
    async def stop(self, ctx):
        """Termina el scrim"""
        self.checking_ids = False
        await ctx.send('El tiempo ha terminado!')
        print('Checking stopped!')


if __name__ == '__main__':
    Bot.run_bot()
