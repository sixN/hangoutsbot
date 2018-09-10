"""
Demonstrates how to use the asyncio compatible scheduler to schedule a job that executes on 3
second intervals.
"""

from datetime import datetime
import os

import hangups

import plugins


from apscheduler.schedulers.asyncio import AsyncIOScheduler

try:
    import asyncio
except ImportError:
    import trollius as asyncio

def _initialise(bot):
    plugins.register_admin_command(["start_tick"])

def tick():
    print('Tick! The time is: %s' % datetime.now())

def start_tick(bot, event, cmd=None, *args):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tick, 'interval', seconds=3)
    scheduler.start()
