from CTFd.plugins.bocx.models import  BOCX_category, BOCX_lockout, BOCXCategoryChallenge, BOCX_selected_cat
from statistics import mode
from sqlalchemy.sql.expression import asc
from CTFd.models import Teams, db, Challenges, Awards, Solves, Users, Submissions
from sqlalchemy.sql import or_, union_all
from CTFd.utils.user import is_admin, get_current_user
from CTFd.utils.scores import get_standings, get_user_standings, get_team_standings
from CTFd.utils.config.visibility import challenges_visible
from CTFd.utils.dates import (
    ctf_started, ctftime, view_after_ctf, unix_time_to_utc
)
from CTFd.cache import cache
from CTFd.utils import get_config
from CTFd.utils.dates import unix_time_to_utc
from CTFd.utils.modes import get_model
from CTFd.utils.config import is_teams_mode, is_users_mode
import decimal
import string
import random
from sqlalchemy.orm import aliased
import json
from pprint import pprint 


#get BOCX CTF Category
def get_category():
    ctf_cat = db.session.query(BOCX_category).first()
    if ctf_cat is None:
        return []
    else:
        return db.session.query(BOCX_category).order_by(BOCX_category.id.asc()).all()

#BOCX CATEGORY LOCKOUT
def get_lockout():
    ctf_cat = db.session.query(BOCX_lockout).first()
    if ctf_cat is None:
        return []
    else:
        return db.session.query(BOCX_lockout).order_by(BOCX_lockout.id.asc()).all()

#get team
def get_teams():
    ctf_team = Teams.query.filter_by(banned=False, hidden=False).first()
    if ctf_team is None:
        return []
    else:
        return Teams.query.filter_by(banned=False, hidden=False).all()


#get challenges by mode user | team
def bocx_challenge():
    chals = ''
    user = get_current_user()
    #prepare team selected category
    selected = aliased(BOCX_selected_cat)
    lockout =  aliased(BOCX_lockout)
    #chals = BOCXCategoryChallenge.query.join(selected,(selected.team_id == user.team_id)
     #       ).filter(BOCXCategoryChallenge.state != 'hidden'
     #       ).filter(BOCXCategoryChallenge.ctf_category_id == selected.ctf_category_id).order_by(BOCXCategoryChallenge.value.asc()).all()
    
    chals = BOCXCategoryChallenge.query.filter(
            or_(BOCXCategoryChallenge.state != 'hidden',BOCXCategoryChallenge.state is None),
            BOCXCategoryChallenge.team_id == user.team_id,
            BOCXCategoryChallenge.ctf_category_id == selected.ctf_category_id,
            BOCXCategoryChallenge.ctf_category_id == lockout.ctf_category_id,
            lockout.lockout_percentage != 1 ).all()
    return chals



#ovveride load chalenges under challenge listing
def get_challenges():
    if not is_admin():
        if not ctftime():
            if view_after_ctf():
                pass
            else:
                return []
   
    if challenges_visible() and (ctf_started() or is_admin()):
        #sort out result
        jchals = []
        results = []
        chals = bocx_challenge()
        if chals: 
           return chals
        #for x in chals:
         #   prereq = []
          #  if x.requirements is None:
           #     req = x.requirements
           # else:
                # req = json.loads( x.requirements )
            #    req = json.dumps( x.requirements )
             #   req = json.loads(req)
              #  for reqs in req['prerequisites']:
               #     if reqs:
                #        val = int(reqs)
                 #       prereq.append({
                  #          'id':val
                   #     })
          #  jchals.append({
           #     'id': x.id,
            #    'name': x.name,
             #   'value': x.value,
              #  'category': x.category,
              #  'description': x.description,
              #  'requirements': prereq,
              #  'category_image': '',
              #  "category_desc": ''
          #  })
        # Sort into groups
     #   xxcat = []
      #  categories = set(map(lambda x: x['category'], jchals))
      #  for xcat in categories:
       #     exist = db.session.query(BOCXCategoryChallenge).filter_by(category=xcat).first()
        #    if exist:
         #       xx = vars(exist)
          #      xxcat.append({
           #     'name': xcat,
            #    'desc': xx['description'],
             #   'image_name': xx['image_name'],
              #  'loc': xx['location']
              #  })
      #  jchals = [j for c in xxcat for j in jchals if j['category'] == c['name']]
      #  results.append({
       #     'categories': xxcat,
        #    'challenges': jchals
       # })
       # return results
    return []
