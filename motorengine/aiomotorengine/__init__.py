try:
    from pymongo import ASCENDING, DESCENDING  # NOQA

    import motorengine.connection
    from functools import partial
    connect = partial(
        motorengine.connection.connect,
        framework=motorengine.connection.FRAMEWORK_ASYNCIO
    )
    disconnect = partial(
        motorengine.connection.disconnect,
        framework=motorengine.connection.FRAMEWORK_ASYNCIO
    )
    get_connection = partial(
        motorengine.connection.get_connection,
        framework=motorengine.connection.FRAMEWORK_ASYNCIO
    )

    from motorengine.aiomotorengine.document import Document  # NOQA

    from motorengine.fields import (  # NOQA
        BaseField, StringField, BooleanField, DateTimeField,
        UUIDField, ListField, EmbeddedDocumentField, ReferenceField, URLField,
        EmailField, IntField, FloatField, DecimalField, BinaryField,
        JsonField
    )

    from motorengine.aiomotorengine.aggregation.base import Aggregation  # NOQA
    from motorengine.query_builder.node import Q, QNot  # NOQA

except ImportError:  # NOQA
    pass  # likely setup.py trying to import version
