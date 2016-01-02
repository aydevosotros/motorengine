from preggy import expect
import unittest

from motorengine import Document, PasswordField
from motorengine.fields.password_field import md5, PasswordType
from tests import AsyncTestCase
from tornado.testing import gen_test


class User(Document):
    __collection__ = 'users'
    password = PasswordField(required=True)


class TestPasswordType(unittest.TestCase):

    def test_md5(self):
        expect(md5('xxx')).to_equal('f561aaf6ef0bf14d4208bb46a4ccb3ad')

    def test_password_type(self):
        x = PasswordType('xxx', crypt_func=md5, is_crypted=False)
        expect(x.value).to_equal('f561aaf6ef0bf14d4208bb46a4ccb3ad')
        expect(x).to_equal('xxx')
        expect(x).not_to_equal('yyy')
        expect(x).not_to_equal(5)

        # test operators ==, !=
        expect(x == 'xxx').to_be_true()
        expect(x != 'yyy').to_be_true()

        y = PasswordType(
            'f561aaf6ef0bf14d4208bb46a4ccb3ad', crypt_func=md5, is_crypted=True
        )
        expect(y).to_equal('xxx')
        expect(y).to_equal(x)

        # test operators ==, !=
        expect(y == x).to_be_true()

        other = PasswordType('other', crypt_func=md5, is_crypted=False)
        expect(y != other).to_be_true()

        z = PasswordType('xxx')
        expect(z).to_equal(x)

    def test_uncrypted_password(self):
        x = PasswordType('xxx', crypt_func=str, is_crypted=False)
        expect(x.value).to_equal('xxx')
        expect(x).to_equal('xxx')


class TestPasswordField(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.drop_coll(User.__collection__)

    def test_password_field(self):
        u = User(password='xxx')

        expect(u.password).to_equal('xxx')

        son = u.to_son()
        expect('password' in son).to_be_true()
        expect(son['password']).to_equal('f561aaf6ef0bf14d4208bb46a4ccb3ad')

    def test_password_field_to_son(self):
        field = PasswordField()

        value = field.to_son(PasswordType('xxx'))
        expect(value).to_equal('f561aaf6ef0bf14d4208bb46a4ccb3ad')

        value = field.to_son('xxx')
        expect(value).to_equal('f561aaf6ef0bf14d4208bb46a4ccb3ad')

    def test_password_field_to_son_wrong_value(self):
        field = PasswordField()
        with expect.error_to_happen(TypeError):
            field.to_son(5)

    @gen_test
    def test_password_field_save_and_load(self):
        user = User(password='xxx')
        result = yield user.save()

        expect(result._id).not_to_be_null()
        expect(user._id).not_to_be_null()

        id = result._id
        # get by id
        user1 = yield User.objects.get(id=id)
        expect(user1).not_to_be_null()
        expect(user1.password).to_equal(user.password)

        # get by passowrd
        user2 = yield User.objects.get(password='xxx')

        expect(user2).not_to_be_null()
        expect(user2._id).to_equal(id)
        expect(user2.password).to_equal('xxx')
        expect(user2.password).to_equal(user.password)

        # test string representation
        expect(str(user2.password)).to_equal('f561aaf6ef0bf14d4208bb46a4ccb3ad')

        # change password with new and save
        user2.password = 'yyy'
        expect(user2.password).to_equal('yyy')
        yield user2.save()

        # try load user with old password
        user3 = yield User.objects.get(password='xxx')
        expect(user3).to_be_null()

        # try load user with new password
        user4 = yield User.objects.get(password='yyy')
        expect(user4).not_to_be_null()
        expect(user4._id).to_equal(id)

    def test_create_password_field(self):
        field = PasswordField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_validate_enforces_password_type(self):
        field = PasswordField()

        expect(field.validate(1)).to_be_false()

    def test_is_empty(self):
        field = PasswordField()
        expect(field.is_empty(None)).to_be_true()
        expect(field.is_empty("")).to_be_true()
        expect(field.is_empty("123")).to_be_false()

    def test_validate_only_if_not_none(self):
        field = PasswordField(required=False)

        expect(field.validate(None)).to_be_true()
