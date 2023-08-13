# bot.py
import os
import discord
import asyncio

from discord.ext import commands

with open("api_key") as file:
    TOKEN = file.readline().strip()

DELETE_QUEUE = set()
CREATE_QUEUE = set()
intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix="*")


@client.command(name="clear_delete_queue", help="Clears the queue of roles to be deleted.")
@commands.has_role('Administrator')
async def clear_delete_queue(ctx):
    DELETE_QUEUE.clear()
    await ctx.send("Cleared delete queue.")


@client.command(name="clear_create_queue", help="Clears the queue of roles to be created.")
@commands.has_role('Administrator')
async def clear_create_queue(ctx):
    CREATE_QUEUE.clear()
    await ctx.send("Cleared create queue.")

@client.command(name="execute", help="First deletes all roles to be deleted. Then creates all roles to be created. Remember these roles have no permissions.")
@commands.has_role('Administrator')
async def execute_queues(ctx):
    guild = ctx.guild
    error_queue = []
    while len(DELETE_QUEUE) > 0:
        role_id = DELETE_QUEUE.pop()
        role = guild.get_role(role_id)
        # make sure the role exists
        if role is not None:
            try:
                await role.delete()
            except:
                # flag it as an error role by adding to error queue
                error_queue.append(role_id)
                continue
            await ctx.send("Deleted role %s" % role.name)
                 
    if len(error_queue) != 0:
        await ctx.send("Some roles were unable to be deleted:\n" + str([guild.get_role(role_id).name for role_id in error_queue]))
    error_queue.clear()
    DELETE_QUEUE.clear()
    while len(CREATE_QUEUE) > 0:
        role_name = CREATE_QUEUE.pop()
        # make sure no role with this name exists
        for role in guild.roles:
            if role.name == role_name:
                await ctx.send("Role named %s already exists!" % role_name)
                continue
        # try creating the role
        try:
            await guild.create_role(name=role_name)
        except:
            # if it errored, flag it by adding it to the error queue
            error_queue.append(role_name)
            continue
        await ctx.send("Created role %s" % role_name)
    if len(error_queue) != 0:
        await ctx.send("Some roles were unable to be created:\n" + str(error_queue))
    
    CREATE_QUEUE.clear()

@client.command(name="dqa", help="Adds role(s) to the delete queue. Multiple roles can be specified in a comment separated list.")
@commands.has_role("Administrator")
async def add_del_role(ctx, *, roles : str):
    role_ids = []
    roles = roles.split(",")
    for role_mention in roles:
        stripped = role_mention.strip(" \n\t@<>&")
        try:
            role_ids.append(int(stripped))
        except:
            await ctx.send("Role `%s` was invalid! Be sure to list roles by @'ing them." % role_mention)
    DELETE_QUEUE.update(role_ids)
    await ctx.send("Added role(s) %s to delete queue" % ["<@&" + str(id) + ">" for id in role_ids])

@client.command(name="cqa", help="Adds role(s) to the create queue. Multiple roles can be specified in a comment separated list.")
@commands.has_role("Administrator")
async def add_create_role(ctx, *, roles : str):
    roles = [role_name.strip(" \n\t") for role_name in roles.split(',')]
    CREATE_QUEUE.update(roles)
    await ctx.send("Added role(s) `%s` to create queue" % roles)

@client.command(name="list", help="Displays the delete and create queues")
@commands.has_role("Administrator")
async def list_queues(ctx):
    await ctx.send("To delete: %s\n To create: %s" % (["<@&" + str(id) + ">" for id in DELETE_QUEUE], str(CREATE_QUEUE)))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command. Must be an admin to invoke.')


client.run(TOKEN)