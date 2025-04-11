from CTFd.models import db, Teams
from CTFd.plugins.bocx.models import  BOCX_category



#get BOCX CTF Category
def get_category():
    ctf_cat = db.session.query(BOCX_category).first()
    if ctf_cat is None:
        return []
    else:
        return db.session.query(BOCX_category).order_by(BOCX_category.id.asc()).all()
#get team
def get_teams():
    ctf_team = Teams.query.filter_by(banned=False, hidden=False).first()
    if ctf_team is None:
        return []
    else:
        return Teams.query.filter_by(banned=False, hidden=False).all()
