# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField,HiddenField, TextAreaField, SelectField, DecimalField, SelectMultipleField, \
    DateTimeField, BooleanField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Regexp, Required, Email, EqualTo
from wtforms import ValidationError
from flask.ext.uploads import UploadSet, IMAGES
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from DB import orm
images = UploadSet('images', IMAGES)


class PageInfo():
    def __init__(self, pagename=""):
        self.pagename = pagename


class RegistrationForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField(u'密码', validators=[Required(), EqualTo('password2', message=u'两次输入必须相同')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    user_type = SelectField(u'用户类型', validators=[Required()] ,choices=[('0', u'房客'),('1', u'房东')])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if orm.User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册')

    def validate_username(self, field):
        if orm.User.query.filter_by(username=field.data).first():
            raise ValidationError(u'该用户已被注册')


class LoginForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')


class PasswordResetForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'新的密码', validators=[
        Required(), EqualTo('password2', message=u'两次密码必须相同')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'重置密码')

    def validate_email(self, field):
        if orm.User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'邮箱地址未知')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('更改密码')


class ChangeUsernameForm(Form):
    username = StringField('新的用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'用户名必须包含字母或数字')])
    submit = SubmitField('保存修改')

    def validate_username(self, field):
        if orm.User.query.filter_by(username=field.data).first():
            raise ValidationError(u'该用户已被注册')

class PasswordResetRequestForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField(u'重置密码')


class BulletinForm(Form):
    id = HiddenField('id')
    # dt = DateTimeField('发布时间', format = '%Y-%m-%d %H:%M:%S')
    title = StringField('标题')
    content = TextAreaField('详情')
    valid = BooleanField('是否有效')
    source = StringField('来源')
    image = FileField('上传图片', validators= [FileAllowed(['jpg', 'png'], 'Images only!')])


class RentForm(Form):
    id = HiddenField('id')
    title = StringField(u'标题', validators=[Required(),Length(1, 64)])
    price = IntegerField(u'租金')
    description= TextAreaField(u'描述')
    area_id = SelectField(u'所在区县', coerce=int)
    mode_id = SelectField(u'出租方式', coerce=int)
    rent_type = SelectField(u'押金方式', validators=[Required()] ,choices=[('0', u'押一付一'),('1', u'押一付三')])
    contacts = StringField(u'联系人')
    phone_number = IntegerField(u'联系方式')
    residential_id = SelectField(u'小区', coerce=int)
    size = StringField(u'面积')
    address= StringField(u'地址')
    subway_line = SelectField(u'地铁线', coerce=int)
    decorate_type = SelectField(u'装修情况', validators=[Required()] ,choices=[('0', u'简单装修'),('1', u'精装修')])
    image = FileField('上传图片', validators= [FileAllowed(['jpg', 'png'], 'Images only!')])


class DemandForm(Form):
    id = HiddenField('id')
    contacts = StringField(u'联系人')
    phone_number = IntegerField(u'联系方式')
    area_id = SelectField(u'所在区县', coerce=int)
    mode_id = SelectField(u'求租方式',coerce=int)
    decorate_type = SelectField(u'装修情况', validators=[Required()] ,choices=[('0', u'简单装修'),('1', u'精装修')])
    subway_line = SelectField(u'附近地铁线', coerce=int)
    price_low = IntegerField(u'最低租金')
    price_high = IntegerField(u'最高租金')
    description = TextAreaField(u'描述')
    title = StringField(u'标题')

    def validate_price_low(self, field):
        if self.price_high.data < self.price_low.data:
            raise ValidationError(u'最低值不能大于最高值')
