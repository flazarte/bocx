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
from CTFd.plugins.bocx.models  import BOCX_category
from CTFd.plugins.bocx.utils import  get_category
from werkzeug.utils import secure_filename
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.models import Challenges, Flags, Solves

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_PATH'] = 'CTFd/plugins/bocx/'
FILE_LOCATON = '/plugins/bocx/writeups/'
FILE_LOCATON_COUNTER = '/plugins/bocx/countermeasure/'
FILE_LOCATON_KNOWLEDGE = '/plugins/bocx/knowledge/'
CATEGORY_FILE_LOCATON = '/plugins/bocx/admin/assets/img/'
bocx = Blueprint('bocx', __name__, static_folder='assets',static_url_path='/plugins/bocx/')
ALLOWED_EXTENSIONS = set(['pdf'])



#routes
@bocx.route('/admin/bocx_settings', methods=['GET'])
@admins_only
def bocx_setting():
    return render_template("plugins/bocx/admin/settings/settings.html",cat=get_category())

#bocx category edit/update/add
@bocx.route('/api/v2/challenge-category/<int:bocx_id>', methods=['GET','POST','DELETE'])
@admins_only
@bypass_csrf_protection
def bocx_category_update_api(bocx_id):
    results = []
    #update data
    if request.method == 'POST':
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
        db.session.commit()
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

#override admin challenges_new
@admins_only
def bocx_challenges_new():
    types = CHALLENGE_CLASSES.keys()
    return render_template("admin/challenges/new.html", types=types, cat=get_category)


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
