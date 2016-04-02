import asyncio
from preggy import expect

from motorengine.aiomotorengine import Document, PasswordField
from tests.aiomotorengine import AsyncTestCase, async_test


class User(Document):
    __collection__ = 'users'
    password = PasswordField(required=True)


class Guest(Document):
    __collection__ = 'guests'
    password = PasswordField(required=False)


class TestPasswordField(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.drop_coll(User.__collection__)

    @async_test
    @asyncio.coroutine
    def test_password_field_save_and_load(self):
        user = User(password='xxx')
        result = yield from user.save()

        expect(result._id).not_to_be_null()
        expect(user._id).not_to_be_null()

        id = result._id
        # get by id
        user1 = yield from User.objects.get(id=id)
        expect(user1).not_to_be_null()
        expect(user1.password).to_equal(user.password)

        # get by passowrd
        user2 = yield from User.objects.get(password='xxx')

        expect(user2).not_to_be_null()
        expect(user2._id).to_equal(id)
        expect(user2.password).to_equal('xxx')
        expect(user2.password).to_equal(user.password)

        # test string representation
        expect(str(user2.password)).to_equal('f561aaf6ef0bf14d4208bb46a4ccb3ad')

        # change password with new and save
        user2.password = 'yyy'
        expect(user2.password).to_equal('yyy')
        yield from user2.save()

        # try load user with old password
        user3 = yield from User.objects.get(password='xxx')
        expect(user3).to_be_null()

        # try load user with new password
        user4 = yield from User.objects.get(password='yyy')
        expect(user4).not_to_be_null()
        expect(user4._id).to_equal(id)

    @async_test
    @asyncio.coroutine
    def test_password_field_not_required_save_and_load(self):
        yield from Guest.objects.delete()
        guest = Guest()
        password = None

        expect(guest.password).to_be_null()
        expect(guest.password == password).to_be_true()
        expect(guest.password is None).to_be_true()
        expect(guest.password == 'xxx').to_be_false()

        yield from guest.save()

        expect(guest._id).not_to_be_null()

        guest = yield from Guest.objects.get(guest._id)

        expect(guest.password).to_be_null()
        expect(guest.password == password).to_be_true()
        expect(guest.password is None).to_be_true()
        expect(guest.password == 'xxx').to_be_false()
