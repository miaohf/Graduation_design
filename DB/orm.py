# coding: utf-8
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import datetime, os, sys
from web.app import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request, url_for
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))
import app


db = SQLAlchemy(app.app)

class Permission:
    Visitor = 0x01
    Renter = 0x02
    Lanlord = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Visitor': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Renter': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    type = db.Column(db.Integer, unique=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions
    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    name = db.Column(db.String(20))
    telephone = db.Column(db.String(50), unique=True)
    role = db.Column(db.Integer)
    flag_telephone = db.Column(db.Integer)
    checkcode = db.Column(db.String(50))
    source = db.Column(db.String(20))
    dtcreate = db.Column(db.DateTime)

    def __init__(self, username=None, password=None, name=None, telephone=None, role=None, flag_telephone=None, checkcode=None, source=None, dtcreate=None):
        self.username = username
        self.password = password
        self.name = name
        self.telephone = telephone
        self.role = role
        self.flag_telephone = flag_telephone
        self.checkcode = checkcode
        self.source = source
        self.dtcreate = dtcreate

    def __repr__(self):
        return '<Account %s>' % self.username


class Test(db.Model):
    user = db.Column(db.String(50), primary_key=True)
    tt = db.Column(db.DateTime())

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return '<Test %s>' % self.user


class Advert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    website = db.Column(db.String(200))
    image_file = db.Column(db.String(200))

    def __init__(self, title, website, image_file):
        self.title = title
        self.website = website
        self.image_file = image_file

    def __repr__(self):
        return '<Advert %s>' % self.title


class Agespan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50, collation='utf8_bin'))
    fromage = db.Column(db.Integer)
    toage = db.Column(db.Integer)

    def __init__(self, name, fromage, toage):
        self.name = name
        self.fromage = fromage
        self.toage = toage

    def __repr__(self):
        return '<Agespan %s>' % self.name


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Area %s>' % self.name


class Bulletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime)
    title = db.Column(db.String(68))
    content = db.Column(db.String(3000))
    valid = db.Integer
    source = db.Column(db.String(68))
    author = db.Column(db.String(68))

    def __init__(self, dt, title, content, source, author):
        self.dt = dt
        self.title = title
        self.content = content
        self.valid = 1
        self.source = source
        self.author = author

    def __repr__(self):
        return '<Bulletin %s>' % self.title


class Bulletinimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bulletin_id = db.Column(db.ForeignKey(u'bulletin.id'))
    file = db.Column(db.String(500))

    bulletin = db.relationship(u'Bulletin', backref = db.backref('bulletinimages', cascade="all, delete-orphan"))

    def __init__(self, bulletin_id, file):
        self.bulletin_id = bulletin_id
        self.file = file

    def __repr__(self):
        return '<Bulletinimage %d,%s>' % (self.bulletin_id, self.file)



class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Feature %s>' % self.name


class Feetype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Feetype %s>' % self.name


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # 品牌名
    agespan_id = db.Column(db.ForeignKey(u'agespan.id')) #招生年龄
    area_id = db.Column(db.ForeignKey(u'area.id')) #区县
    address = db.Column(db.String(100)) #校区地址
    location = db.Column(db.String(100)) # 校区名
    website = db.Column(db.String(100)) #网址
    telephone = db.Column(db.String(50)) #电话
    feedesc = db.Column(db.String(100)) # 学费标准
    timeopen = db.Column(db.DateTime) #开业时间
    timeclose = db.Column(db.DateTime) #关门y时间
    feetype_id = db.Column(db.ForeignKey(u'feetype.id'))
    longitude = db.Column(db.Float) #经度
    latitude = db.Column(db.Float)  #纬度
    featuredesc = db.Column(db.String(200)) #特色小项描述

    feetype = db.relationship(u'Feetype')
    area = db.relationship(u'Area')
    agespan = db.relationship(u'Agespan')

    def __init__(self, name, agespan_id, area_id, address, location, website, telephone, feedesc, timeopen, timeclose, feetype_id, longitude, latitude, featuredesc):
        self.name = name
        self.agespan_id = agespan_id
        self.area_id = area_id
        self.address = address
        self.location = location
        self.website = website
        self.telephone = telephone
        self.feedesc = feedesc
        self.timeopen = timeopen
        self.timeclose = timeclose
        self.feetype_id = feetype_id
        self.longitude = longitude
        self.latitude = latitude
        self.featuredesc = featuredesc

    def __repr__(self):
        return '<Institution %s>' % self.name


class InstitutionFeature(db.Model):
    institution_id = db.Column(db.ForeignKey(u'institution.id'), primary_key=True)
    feature_id = db.Column(db.ForeignKey(u'feature.id'), primary_key=True)

    institution = db.relationship(u'Institution', backref = db.backref('institutionfeatures', cascade="all, delete-orphan"))
    feature = db.relationship(u'Feature')

    def __init__(self, institution_id, feature_id):
        self.institution_id = institution_id
        self.feature_id = feature_id

    def __repr__(self):
        return '<InstitutionFeature %s>' % self.name


class Institutionimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.ForeignKey(u'institution.id'))
    file = db.Column(db.String(500))

    institution = db.relationship(u'Institution', backref = db.backref('institutionimages', cascade="all, delete-orphan"))

    def __init__(self, institution_id, file):
        self.institution_id = institution_id
        self.file = file

    def __repr__(self):
        return '<Institutionimage %d,%s>' % (self.institution_id, self.file)


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # 学校名称
    area_id = db.Column(db.ForeignKey(u'area.id')) #区县
    teachdesc = db.Column(db.Text) #校长及教师情况
    address = db.Column(db.String(100)) #地址
    schooltype_id = db.Column(db.ForeignKey(u'schooltype.id')) #学校性质
    website = db.Column(db.String(100)) #网址
    distinguish = db.Column(db.Text) #教学特色
    leisure = db.Column(db.String(1000)) #课外特色活动
    threashold = db.Column(db.String(1000)) #招生条件及招生地块
    partner = db.Column(db.String(100)) #对口学校
    artsource = db.Column(db.String(1000)) # 艺术特长招生数量
    feedesc = db.Column(db.String(100)) #学费标准
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)


    schooltype = db.relationship(u'Schooltype')
    area = db.relationship(u'Area')


    def __init__(self, name, area_id, teachdesc, address, schooltype_id, website, distinguish, leisure, threashold, partner, artsource, feedesc, longitude, latitude):
        self.name = name
        self.area_id = area_id
        self.teachdesc = teachdesc
        self.address = address
        self.schooltype_id = schooltype_id
        self.website = website
        self.distinguish = distinguish
        self.leisure = leisure
        self.threashold = threashold
        self.partner = partner
        self.artsource = artsource
        self.feedesc = feedesc
        self.longitude = longitude
        self.latitude = latitude


    def __repr__(self):
        return '<School %s>' % self.name



class SchoolFeature(db.Model):
    school_id = db.Column(db.ForeignKey(u'school.id'), primary_key=True)
    feature_id = db.Column(db.ForeignKey(u'feature.id'), primary_key=True)

    school = db.relationship(u'School', backref = db.backref('schoolfeatures', cascade="all, delete-orphan"))
    feature = db.relationship(u'Feature')

    def __init__(self, school_id, feature_id):
        self.school_id = school_id
        self.feature_id = feature_id

    def __repr__(self):
        return '<SchoolFeature %d,%d>' % (self.school_id, self.feature_id)


class Schoolimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.ForeignKey(u'school.id'))
    file = db.Column(db.String(500))

    school = db.relationship(u'School', backref = db.backref('schoolimages', cascade="all, delete-orphan"))

    def __init__(self, school_id, file):
        self.school_id = school_id
        self.file = file

    def __repr__(self):
        return '<Schoolimage %d,%s>' % (self.school_id, self.file)


class Schooltype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Schooltype %s>' % self.name


class Terminal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.ForeignKey(u'account.id'))
    os = db.Column(db.String(20))
    code = db.Column(db.String(255))

    account = db.relationship(u'Account', backref = db.backref('terminals'))

    def __init__(self, account_id, os=None, code=None):
        self.account_id = account_id
        self.os = os
        self.code = code

    def __repr__(self):
        return '<Terminal %d,%d,%s>' % (self.account_id, self.type, self.code)


class Residential(db.Model):
    __tablename__ = 'residential'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Residential %s>' % self.name


class Rent(db.Model):
    __tablename__ = 'rent'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))  # 标题
    price = db.Column(db.Integer)  # 价格
    description = db.Column(db.Text)  # 描述
    area_id = db.Column(db.ForeignKey(u'area.id'))  # 区县
    rent_type = db.Column(db.Integer)  # 类型
    rental_mode = db.Column(db.String(20))  # (整租，单间，合租)
    contacts = db.Column(db.String(20))  # 联系人
    phone_number = db.Column(db.Integer)   # 联系方式
    date = db.Column(db.DateTime)   # 发布日期
    residential_id = db.Column(db.ForeignKey(u'residential.id'))  # 小区名称
    size = db.Column(db.String(20))    # 面积
    address = db.Column(db.String(50))  # 地址
    subway_line = db.Column(db.ForeignKey(u'subway.id'))  # 地铁几号线附近
    decorate_type = db.Column(db.Boolean)  # 装修类型
    # 房屋类型
    residential = db.relationship(u'Residential')
    area = db.relationship(u'Area')
    subway = db.relationship(u'Subway')

    def __init__(self, area_id, title, price, description, rent_type, rental_mode, contacts, phone_number, date,
                 residential_id, size, address, decorate_type, subway_line):
        self.area_id = area_id
        self.title = title
        self.price = price
        self.description = description
        self.rent_type = rent_type
        self.rental_mode = rental_mode
        self.contacts = contacts
        self.phone_number = phone_number
        self.date = date
        self.residential_id = residential_id
        self.size = size
        self.address = address
        self.decorate_type = decorate_type
        self.subway_line = subway_line

    def __repr__(self):
        return '<Rent %s>' % self.name


class Rentimage(db.Model):
    __tablename__ = 'rentimages'
    id = db.Column(db.Integer, primary_key=True)
    rent_id = db.Column(db.ForeignKey(u'rent.id'))
    file = db.Column(db.String(500))

    rent = db.relationship(u'Rent', backref=db.backref('rentimages', cascade="all, delete-orphan"))

    def __init__(self, rent_id, file):
        self.rent_id = rent_id
        self.file = file

    def __repr__(self):
        return '<Rentimage %d,%s>' % (self.rent_id, self.file)


class Demand(db.Model):
    __tablename__ = 'demand'
    id = db.Column(db.Integer, primary_key=True)
    price_low = db.Column(db.Integer)  # 最低价格
    price_high = db.Column(db.Integer)  # 最高价格
    area_id = db.Column(db.ForeignKey(u'area.id'))  # 区县
    contacts = db.Column(db.String(20))  # 联系人
    phone_number = db.Column(db.Integer)  # 联系方式
    rental_mode = db.Column(db.String(20))  # (整租，单间，合租)
    decorate_type = db.Column(db.Boolean)  # 装修类型
    subway_line = db.Column(db.ForeignKey(u'subway.id'))  # 地铁几号线附近
    description = db.Column(db.Text)  # 描述
    date = db.Column(db.DateTime)  # 发布日期
    title = db.Column(db.String(50))  # 标题

    area = db.relationship(u'Area')
    subway = db.relationship(u'Subway')

    def __init__(self, price_low, price_high, area_id, contacts, phone_number, rental_mode, decorate_type, subway_line,
                 description, date, title):
        self.price_high = price_high
        self.price_low = price_low
        self.area_id = area_id
        self.contacts = contacts
        self.phone_number = phone_number
        self.rental_mode = rental_mode
        self.decorate_type = decorate_type
        self.subway_line = subway_line
        self.description = description
        self.date = date
        self.title = title

    def __repr__(self):
        return '<Demand %s>' % self.name


class Subway(db.Model):
    __tablename__ = 'subway'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Subway %s>' % self.name
