#-*- coding: utf-8 -*-
import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../..'))


reload(sys)
sys.setdefaultencoding('utf-8')
from DB import orm
from forms import SchoolForm, BulletinForm, AccountForm, RentForm, RegistrationForm, DemandForm
from Logic import restful


g_choices_area = [(g.id, g.name) for g in orm.Area.query.order_by('name')]
g_choices_residential = [(g.id, g.name) for g in orm.Residential.query.order_by('name')]
g_choices_subway = [(g.id, g.name) for g in orm.Subway.query.order_by('id')]
g_choices_mode = [(g.id, g.name) for g in orm.Mode.query.order_by('id')]
g_choices_schooltype = [(g.id, g.name) for g in orm.Schooltype.query.order_by('name')]
g_choices_feature = [(g.id, g.name) for g in orm.Feature.query.order_by('name')]
g_choices_agespan = [(g.id, g.name) for g in orm.Agespan.query.order_by('name')]
g_choices_feetype = [(g.id, g.name) for g in orm.Feetype.query.order_by('name')]


def GetRentFormById(rent_id):
    rent = orm.Rent.query.get(int(rent_id))
    if rent is None:
        return None
    rentform = RentForm()
    if rent.rentimages != []:
        rentform.image.data = rent.rentimages[0].file
    else:
        rentform.image.date = []
    rentform.id.data = rent.id
    rentform.area_id.data = rent.area_id
    rentform.area_name = rent.area.name
    rentform.subway_name = rent.subway.name
    rentform.price.data = rent.price
    rentform.description.data = rent.description
    rentform.contacts.data = rent.contacts
    rentform.phone_number.data = rent.phone_number
    rentform.title.data = rent.title
    rentform.mode_id.data = rent.mode_id
    rentform.rent_type.data = rent.rent_type
    rentform.address.data = rent.address
    rentform.area_id.choices = g_choices_area
    rentform.mode_id.choices = g_choices_mode
    rentform.residential_id.choices = g_choices_residential
    rentform.subway_line.choices = g_choices_subway
    return rentform


def GetDemandFormById(demand_id):
    demand = orm.Demand.query.get(int(demand_id))
    if demand is None:
        return None
    demandform = DemandForm()

    demandform.id.data = demand.id
    demandform.area_id.data = demand.area_id
    demandform.area_name = demand.area.name
    demandform.subway_name = demand.subway.name
    demandform.price_high.data = demand.price_high
    demandform.price_low.data = demand.price_low
    demandform.description.data = demand.description
    demandform.contacts.data = demand.contacts
    demandform.phone_number.data = demand.phone_number
    demandform.decorate_type.data = demand.decorate_type
    demandform.title.data = demand.title
    demandform.mode_id.data = demand.mode_id
    demandform.rent_type.data = demand.rent_type
    demandform.area_id.choices = g_choices_area
    demandform.subway_line.choices = g_choices_subway
    return demandform

def GetSchoolFormById(school_id):
    school = orm.School.query.get(int(school_id))
    if school is None: return None
    schoolform = SchoolForm()
    schoolform.id.data = school.id
    schoolform.name.data = school.name
    schoolform.area_id.data = school.area_id
    schoolform.area_name = school.area.name
    schoolform.teachdesc.data = school.teachdesc
    schoolform.address.data = school.address
    schoolform.schooltype_id.data = school.schooltype_id
    schoolform.schooltype_name = school.schooltype.name
    schoolform.website.data = school.website
    schoolform.distinguish.data = school.distinguish
    schoolform.leisure.data = school.leisure
    schoolform.threashold.data =school.threashold
    schoolform.partner.data = school.partner
    schoolform.artsource.data = school.artsource
    schoolform.feedesc.data = school.feedesc
    schoolform.longitude.data =school.longitude
    schoolform.latitude.data = school.latitude
    schoolform.schoolimages = school.schoolimages
    schoolform.feature_ids.data = [x.feature_id for x in school.schoolfeatures]

    schoolform.area_id.choices = g_choices_area
    schoolform.schooltype_id.choices = g_choices_schooltype
    schoolform.feature_ids.choices = g_choices_feature
    return schoolform


def SetInstitutionFeatures(institution_id, feature_ids):
    for x in orm.InstitutionFeature.query.filter_by(institution_id=institution_id).all():
        orm.db.session.delete(x)
    for x in feature_ids:
        sf = orm.InstitutionFeature(institution_id, x)
        orm.db.session.add(sf)
    orm.db.session.commit()


def GetBulletinFormById(bulletin_id):
    bulletin = orm.Bulletin.query.get(int(bulletin_id))
    if bulletin is None: return None
    bulletinform = BulletinForm()
    bulletinform.id.data = bulletin.id
    bulletinform.title.data = bulletin.title
    bulletinform.content.data = bulletin.content
    bulletinform.dt.data = bulletin.dt
    bulletinform.valid.data = bulletin.valid
    bulletinform.source.data = bulletin.source
    bulletinform.author.data = bulletin.author
    return bulletinform


def GetAccountFormById(account_id):
    account = orm.Account.query.get(int(account_id))
    if account is None: return None
    accountform = AccountForm()
    accountform.id.data = account.id
    accountform.username.data = account.username
    accountform.password.data = account.password
    accountform.name.data = account.name
    accountform.telephone.data = account.telephone
    accountform.flag_telephone.data = True if account.flag_telephone >0 else False
    accountform.checkcode.data = account.checkcode
    accountform.source.data = account.source
    accountform.dtcreate.data = account.dtcreate
    return accountform


def GetUserFormById(user_id):
    user = orm.User.query.get(int(user_id))
    if user is None:
        return None
    userform = RegistrationForm()
    userform.id.data = user.id
    userform.username.data = user.username
    userform.email.data = user.email
    userform.user_type.data = user.user_type
    return userform


def LoadBasePageInfo(pagename, form):
    form.pagename = pagename;
    form.rent_count = orm.Rent.query.count()
    form.demand_count = orm.Demand.query.count()
    form.bulletin_count = orm.Bulletin.query.count()
    form.user_count = orm.User.query.count()


def SetDefaultImage(obj):
    if obj.has_key(restful.ITEM_BULLETINIMAGES):
        listimage = obj.get(restful.ITEM_BULLETINIMAGES,[])
        if len(listimage)<=0:
            listimage.append({restful.ITEM_ID:0,restful.ITEM_FILE:'default_bulletinimage.jpg'})

    if obj.has_key(restful.ITEM_INSTITUTIONIMAGES):
        listimage = obj.get(restful.ITEM_INSTITUTIONIMAGES,[])
        if len(listimage)<=0:
            listimage.append({restful.ITEM_ID:0,restful.ITEM_FILE:'default_institutionimage.jpg'})

    if obj.has_key(restful.ITEM_SCHOOLIMAGES):
        listimage = obj.get(restful.ITEM_SCHOOLIMAGES,[])
        if len(listimage)<=0:
            listimage.append({restful.ITEM_ID:0,restful.ITEM_FILE:'default_schoolimage.jpg'})

if __name__ == '__main__':
    print orm.Area.query.get(1)


