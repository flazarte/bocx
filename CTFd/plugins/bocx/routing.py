import os, json
from CTFd.models import db
from flask import (
    render_template,
    jsonify,
    Blueprint,
    url_for,
    redirect,
    request,
    session,
    Flask,
    abort,
)
from CTFd.utils.decorators import admins_only
from CTFd.plugins import bypass_csrf_protection
from CTFd.plugins.bocx.models  import BOCX_category, BOCX_lockout, BOCXCategoryChallenge, BOCX_selected_cat, BOCX_team_servers
from CTFd.plugins.bocx.utils import  get_category, get_lockout, get_teams, get_challenges
from werkzeug.utils import secure_filename
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.models import Challenges, Flags, Solves, Teams
from CTFd.utils.user import is_admin, authed, get_current_user, get_current_team, get_current_user_attrs
from CTFd.utils.decorators import (
    authed_only,
    during_ctf_time_only,
    require_complete_profile,
    require_verified_emails,
)
from CTFd.utils.decorators.visibility import check_challenge_visibility, check_account_visibility, check_score_visibility
from CTFd.constants.config import ChallengeVisibilityTypes, Configs
from CTFd.utils.helpers import get_errors, get_infos
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started
from CTFd.utils.config import is_teams_mode
from CTFd.utils.config.pages import build_markdown, get_page
from CTFd.utils.decorators.modes import require_team_mode
from pprint import pprint 

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_PATH'] = 'CTFd/plugins/bocx/'
FILE_LOCATON = '/plugins/bocx/writeups/'
FILE_LOCATON_COUNTER = '/plugins/bocx/countermeasure/'
FILE_LOCATON_KNOWLEDGE = '/plugins/bocx/knowledge/'
CATEGORY_FILE_LOCATON = '/plugins/bocx/admin/assets/img/'
bocx = Blueprint('bocx', __name__, static_folder='assets',static_url_path='/plugins/bocx/')
ALLOWED_EXTENSIONS = set(['pdf'])



#routes
@bocx.route('/admin/bocx_settings', methods=['GET', 'POST'])
@admins_only
@bypass_csrf_protection
def bocx_setting():
    results = []
    teams=Teams.query.filter_by(banned=False, hidden=False).all()
    servers=db.session.query(BOCX_team_servers).all() 
    if request.method == 'POST': 
       bocx_server_add = request.form.get('bocx-server-add', None)
       if bocx_server_add != None:
           ctf_category_id = request.form['ctf_category_id']
           team_id  = request.form['team_id']
           server_name = request.form['server_name']
           server_username = request.form['server_username']
           server_password = request.form['server_password']
           server_description = request.form['server_description']
           server_host = request.form['server_host']
           server_image_name = request.form['server_image_name']
           if request.files['server_image_name']:
               cat_image = request.files['server_image_name']
               filename = secure_filename(cat_image.filename)
               cat_image.save(os.path.join(app.config['UPLOAD_PATH']+"admin/assets/img", filename))
               loc = CATEGORY_FILE_LOCATON+filename
               add_server = BOCX_team_servers(server_name=server_name,ctf_category_id=ctf_category_id,team_id=team_id,server_username=server_username,server_password=server_password,server_description=server_description,server_host=server_host,server_image_name=filename,server_image_location=loc)
               db.session.add(add_server)
               db.session.commit()
               #return redirect(request.referrer)
               return jsonify(results)        
           add_server = BOCX_team_servers(server_name=server_name,ctf_category_id=ctf_category_id,team_id=team_id,server_username=server_username,server_password=server_password,server_description=server_description,server_host=server_host)
           db.session.add(add_server)
           db.session.commit()
       return jsonify(results)
       #return redirect(request.referrer)
    return render_template("plugins/bocx/admin/settings/settings.html",cat=get_category(), lockout=get_lockout(), teams=teams, servers=servers)

#bocx category edit/update/add
@bocx.route('/api/v2/challenge-category/<int:bocx_id>', methods=['GET','POST','DELETE'])
@admins_only
@bypass_csrf_protection
def bocx_category_update_api(bocx_id):
    results = []
    #update data
    if request.method == 'POST':
        #ADD Category
        bocx_update = request.form.get('bocx-category', None)
        if bocx_update != None:
            if request.form['bocx-category'] == 'true':
                cat_name = request.form['challenge-bocx-category-name']
                cat_desc = request.form['challenge-bocx-category-description']
                if request.files['bocx_image']:
                    cat_image = request.files['bocx_image']
                    filename = secure_filename(cat_image.filename)
                    cat_image.save(os.path.join(app.config['UPLOAD_PATH']+"admin/assets/img", filename))
                    loc = CATEGORY_FILE_LOCATON+filename
                    doc_exist = db.session.query(BOCX_category).filter_by(id = bocx_id).first()
                    if doc_exist is None:
                        db.session.merge(BOCX_category(category = cat_name, description = cat_desc,location=loc, image_name = filename))
                    else:
                        db.session.query(BOCX_category).filter_by(id = bocx_id).update(dict(category = cat_name, description = cat_desc, location=loc, image_name = filename))
                else:
                    doc_exist = db.session.query(BOCX_category).filter_by(id = bocx_id).first()
                    if doc_exist is None:
                        db.session.merge(BOCX_category(category = cat_name, description = cat_desc))
                    else:
                        db.session.query(BOCX_category).filter_by(id = bocx_id).update(dict(category = cat_name, description = cat_desc))
                lockout = request.form['lockout']
                if lockout:
                   lock_exist = db.session.query(BOCX_lockout).filter_by(ctf_category_id  = bocx_id).first()
                   if lock_exist is None:
                        db.session.merge(BOCX_lockout(lockout_percentage = lockout, ctf_category_id  = bocx_id))
                   else:
                        db.session.query(BOCX_lockout).filter_by(ctf_category_id  = bocx_id).update(dict(lockout_percentage = lockout))
        db.session.commit()
        #Cetgory Add
        bocx_add = request.form.get('bocx-category-add', None)
        if bocx_add != None:
             cat_name = request.form['challenge-bocx-category-name']
             cat_desc = request.form['challenge-bocx-category-description']
             cat = BOCX_category(category=cat_name,description=cat_desc)
             db.session.add(cat)
             db.session.commit()
             results.append({
                    'success': True,
                    'form': bocx_add
                })
             return jsonify(results)
        return redirect(request.referrer)
        
    #delete Data
    if request.method == 'DELETE':
        db.session.query(BOCX_category).filter_by(id = bocx_id).delete()
        db.session.commit()
        results.append({
                    'success': True
                })
        return jsonify(results)

    #fetch data
    if request.method == 'GET':
        if bocx_id > 0:
           cat = db.session.query(BOCX_category).filter_by(id = bocx_id).first()
           results.append({
               'id': cat.id,
               'category': cat.category,
               'description': cat.description,
               'image_name': cat.image_name,
               'location': cat.location    
            })
           return jsonify(results)
        else:
           cat_exist = db.session.query(BOCX_category).order_by(BOCX_category.id.asc()).all()
           if cat_exist:
              for cat in cat_exist:
                   results.append({
                       'id': cat.id,
                       'category': cat.category,
                       'description': cat.description,
                       'image_name': cat.image_name,
                       'location': cat.location    
                   })
              return jsonify(results)
    return jsonify(results)

#bocx challenge  edit/update
@bocx.route('/api/v2/challenge-update/<int:challenge_id>', methods=['POST'])
@admins_only
@bypass_csrf_protection
def bocx_challenge_update_api(challenge_id):
    results=False
    if request.method == 'POST':
        ctf_category_id = request.form['ctf_category_id']
        team_id = request.form['team_id']
        db.session.query(BOCXCategoryChallenge).filter_by(id = challenge_id).update(dict(ctf_category_id = ctf_category_id, team_id = team_id))
        results=True
    return jsonify(results)

#override admin challenges_new
@admins_only
def bocx_challenges_new():
    types = CHALLENGE_CLASSES.keys()
    return render_template("admin/challenges/new.html", types=types, cat=get_category)


#get Bocx Teams
@bocx.route('/api/v2/bocx_teams', methods=['GET'])
@admins_only
@bypass_csrf_protection
def bocx_get_team_api():
    results = []
    teams = get_teams()
    if teams:
        for x in teams:
            results.append({
                'id': x.id,
                'name': x.name    
            })
        return jsonify(results)
    return jsonify(results)

#get challenge detail
@admins_only
def bocx_challenges_detail(challenge_id):
    results = []
    challenges = dict(
        Challenges.query.with_entities(Challenges.id, Challenges.name).all()
    )
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    solves = (
        Solves.query.filter_by(challenge_id=challenge.id)
        .order_by(Solves.date.asc())
        .all()
    )
    flags = Flags.query.filter_by(challenge_id=challenge.id).all()
  

    try:
        challenge_class = get_chal_class(challenge.type)
    except KeyError:
        abort(
            500,
            f"The underlying challenge type ({challenge.type}) is not installed. This challenge can not be loaded.",
        )

    update_j2 = render_template(
        challenge_class.templates["update"].lstrip("/"), challenge=challenge
    )

    update_script = url_for(
        "views.static_html", route=challenge_class.scripts["update"].lstrip("/")
    )

    return render_template(
        "admin/challenges/challenge.html",
        update_template=update_j2,
        update_script=update_script,
        challenge=challenge,
        challenges=challenges,
        solves=solves,
        flags=flags,
    )

def bocx_challenges_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    filters = []

    if q:
        # The field exists as an exposed column
        if Challenges.__mapper__.has_property(field):
            filters.append(getattr(Challenges, field).like("%{}%".format(q)))

    query = Challenges.query.filter(*filters).order_by(Challenges.id.asc())
    challenges = query.all()
    total = query.count()
    #bocx_cat = db.session.query(BOCXCategoryChallenge).filter_by(id = challenge_id).first()

    return render_template(
        "admin/challenges/challenges.html",
        challenges=challenges,
        total=total,
        q=q,
        field=field,
    )


@admins_only
def get_CTF_name(bocx_id):
    cat = BOCX_category.query.get(bocx_id)
    return cat.category if cat else None

@admins_only
def get_bocx_team_name(team_id):
    team = Teams.query.get(team_id)
    return team.name if team else None

def get_bocx_team_country(team_id):
    team = Teams.query.get(team_id)
    return team.country if team else None


#OVERIDE CHALLENGES
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
@check_challenge_visibility
def bocx_chal_listing():
    #pprint(get_challenges())
    user = get_current_user()
    cat_exist = db.session.query(BOCX_selected_cat).filter_by(team_id = user.team_id).first()
    if cat_exist is None:
        return redirect("ctf-category", code=303)
    if cat_exist.team_id is None: 
        return redirect("ctf-category", code=303)
    if (
        Configs.challenge_visibility == ChallengeVisibilityTypes.PUBLIC
        and authed() is False
    ):
        pass
    else:
        if is_teams_mode() and  get_current_team() is None:
            return redirect(url_for("teams.private", next=request.full_path))

    infos = get_infos()
    errors = get_errors()

    if Configs.challenge_visibility == ChallengeVisibilityTypes.ADMINS:
        infos.append("Challenge Visibility is set to Admins Only")

    if ctf_started() is False:
        errors.append(f"{Configs.ctf_name} has not started yet")

    if ctf_paused() is True:
        infos.append(f"{Configs.ctf_name} is paused")

    if ctf_ended() is True:
        infos.append(f"{Configs.ctf_name} has ended")

    return render_template("challenges.html", results = get_challenges(), infos=infos, errors=errors, user=user)



@bocx.route('/ctf-category',methods=['GET'])
@require_team_mode
@authed_only
def bocx_view_challenge_category():
    user = get_current_user()
    cat_exist = db.session.query(BOCX_selected_cat).filter_by(team_id = user.team_id).first()
    if not authed():
        return redirect(url_for('auth.login', next=request.path))
    if get_current_team() is None:
        return redirect(url_for("teams.private", next=request.full_path))
    if request.method == 'POST':
        if cat_exist is None:
           db.session.merge(BOCX_selected_cat(ctf_category_id = cat_id, team_id = user.team_id))
        else:
           db.session.query(BOCX_selected_cat).filter_by(team_id = user.team_id).update(dict(ctf_category_id = cat_id))
        db.session.commit()
        return redirect(url_for('challenges.listing'))
    return render_template('plugins/bocx/templates/ctf-category.html',cat=get_category(), lockout=get_lockout())


@bocx.route('/api/v2/ctf-category/<int:cat_id>', methods=['POST', 'GET'])
@authed_only
@bypass_csrf_protection
def bocx_view_challenge_category_api(cat_id):
    results=[]
    user = get_current_user()
    cat_exist = db.session.query(BOCX_selected_cat).filter_by(team_id = user.team_id).first()
    if not authed():
        return redirect(url_for('auth.login', next=request.path))
    if get_current_team() is None:
        return redirect(url_for("teams.private", next=request.full_path))
    if request.method == 'POST':
        if cat_exist is None:
           db.session.merge(BOCX_selected_cat(ctf_category_id = cat_id, team_id = user.team_id))
        else:
           db.session.query(BOCX_selected_cat).filter_by(team_id = user.team_id).update(dict(ctf_category_id = cat_id))
        db.session.commit()
        results.append({
                    'success': True
                })
       # return redirect(url_for('challenges.listing'))
    return jsonify(results)

#new index home pagee
@bocx.route("/", defaults={"route": "index"})
@bocx.route("/<path:route>")
def bocx_static_html(route):
    """
    Route in charge of routing users to Pages.
    :param route:
    :return:
    """
    page = get_page(route)
    if page is None:
        abort(404)
    else:
        if page.auth_required and authed() is False:
            return redirect(url_for("auth.login", next=request.full_path))

        return render_template("plugins/bocx/templates/index.html", content=page.html, title=page.title)




@check_account_visibility
@admins_only
def new_users_listing():
    q = request.args.get("q")
    field = request.args.get("field", "name")
    if field not in ("name", "affiliation", "website"):
        field = "name"

    filters = []
    if q:
        filters.append(getattr(Users, field).like("%{}%".format(q)))

    users = (
        Users.query.filter_by(banned=False, hidden=False)
        .filter(*filters)
        .order_by(Users.id.asc())
        .paginate(per_page=50, error_out=False)
    )

    args = dict(request.args)
    args.pop("page", 1)

    return render_template(
        "users/users.html",
        users=users,
        prev_page=url_for(request.endpoint, page=users.prev_num, **args),
        next_page=url_for(request.endpoint, page=users.next_num, **args),
        q=q,
        field=field,
    )

@check_account_visibility
@check_score_visibility
@admins_only
def new_public(user_id):
    infos = get_infos()
    errors = get_errors()
    user = Users.query.filter_by(id=user_id, banned=False, hidden=False).first_or_404()

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    return render_template(
        "users/public.html", user=user, account=user.account, infos=infos, errors=errors
    )

@check_account_visibility
@check_score_visibility
@require_team_mode
@admins_only
def new_team_public(team_id):
    infos = get_infos()
    errors = get_errors()
    team = Teams.query.filter_by(id=team_id, banned=False, hidden=False).first_or_404()
    solves = team.get_solves()
    awards = team.get_awards()

    place = team.place
    score = team.score

    if errors:
        return render_template("teams/public.html", team=team, errors=errors)

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    return render_template(
        "teams/public.html",
        solves=solves,
        awards=awards,
        team=team,
        score=score,
        place=place,
        score_frozen=config.is_scoreboard_frozen(),
        infos=infos,
        errors=errors,
    )

@bocx.route('/ctf-servers',methods=['GET'])
@require_team_mode
@authed_only
def bocx_view_challenge_servers():
    user = get_current_user()
    cat_exist = db.session.query(BOCX_selected_cat).filter_by(team_id = user.team_id).first()
    if not authed():
        return redirect(url_for('auth.login', next=request.path))
    if get_current_team() is None:
        return redirect(url_for("teams.private", next=request.full_path))
    if request.method == 'POST':
        if cat_exist is None:
           db.session.merge(BOCX_selected_cat(ctf_category_id = cat_id, team_id = user.team_id))
        else:
           db.session.query(BOCX_selected_cat).filter_by(team_id = user.team_id).update(dict(ctf_category_id = cat_id))
        db.session.commit()
        return redirect(url_for('challenges.listing'))
    teams=Teams.query.filter_by(banned=False, hidden=False).first_or_404()
    #get all servers machine inventory for each CTF Team
    servers = db.session.query(BOCX_team_servers).all()
    return render_template('plugins/bocx/templates/bocx-servers.html',cat=get_category(), lockout=get_lockout(), teams=teams)
