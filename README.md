motorengine
===========

[![Build Status](https://travis-ci.org/ilex/motorengine.svg?branch=asyncio)](https://travis-ci.org/ilex/motorengine)

motorengine is a port of the incredible mongoengine mapper, using Motor for asynchronous access to mongo.

It's an `asyncio` branch which contains `motorengine.aiomotorengine` to use `motorengine` with `asyncio`

Find out more by reading [motorengine documentation](http://motorengine.readthedocs.org/en/latest/).

Getting started with asyncio
============================

Use `motorengine.aiomotorengine` instead of `motorengine` and `await` instead of `yield`
throughout the documentation.

```python
import asyncio

from motorengine.aiomotorengine import Document, StringField, connect


class User(Document):
    name = StringField(required=True)


async def go():
    bernardo = await User(name='Bernardo').save()
    someone = await User.objects.create(name='Someone')

    user = await User.objects.get(bernardo._id)
    assert user.name == 'Bernardo'

    users = await User.objects.filter(name='Someone').find_all()
    assert len(users) == 1
    assert users[0].name == 'Someone'


loop = asyncio.get_event_loop()
connect("test", host="localhost", port=27017, io_loop=loop)

loop.run_until_complete(go())
```
