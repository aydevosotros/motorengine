import asyncio
from easydict import EasyDict as edict

import motorengine


class Aggregation(motorengine.Aggregation):
    __doc__ = motorengine.Aggregation.__doc__

    @asyncio.coroutine
    def fetch(self, alias=None):
        coll = self.queryset.coll(alias)
        results = []
        try:
            # from motor-0.5 coll.aggregate return AsyncIOMotorAggregateCursor
            lst = yield from coll.aggregate(self.to_query(), cursor=False)
            for item in lst['result']:
                self.fill_ids(item)
                results.append(edict(item))
        except Exception as e:
            raise RuntimeError('Aggregation failed due to: %s' % str(e))
        return results
