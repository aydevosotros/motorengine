import asyncio
import motorengine.database


class Database(motorengine.database.Database):

    @asyncio.coroutine
    def ping(self):
        return (yield from self.connection.admin.command('ping'))
