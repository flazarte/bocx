import os
from flask import Blueprint
from CTFd.models import db, Challenges, Flags
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.plugins.challenges import BaseChallenge
from CTFd.plugins import override_template, register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.bocx.routing import bocx, bocx_setting, bocx_category_update_api, bocx_challenges_new, bocx_challenges_detail 
from CTFd.plugins.bocx.models import CategoryGameClass





def load(app):
    app.db.create_all()
    app.register_blueprint(bocx)

    CHALLENGE_CLASSES["bocx_category"] = CategoryGameClass
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #override teemplates
   # admin_new_challenges = os.path.join(dir_path, 'admin/challenges/new.html')
   # override_template('admin/challenges/new.html', open(admin_new_challenges).read())
   # admin_new_challenge = os.path.join(dir_path, 'admin/challenges/challenge.html')
   # override_template('admin/challenges/challenge.html', open(admin_new_challenge).read())
    #admin_base
    #admin_base = os.path.join(dir_path, 'admin/base.html')
    #override_template('admin/base.html', open(admin_base).read())
    #admin bocx setting
    app.view_functions['bocx.settings'] = bocx_setting
    app.add_url_rule('/api/v2/challenge-category/<int:bocx_id>', 'bocx.bocx_update_api',bocx_category_update_api)
    #api routes
    app.view_functions['bocx.bocx_update_api'] = bocx_category_update_api
    #override routes
    app.view_functions['admin.challenges_new'] = bocx_challenges_new
    app.view_functions['admin.challenges_detail'] = bocx_challenges_detail
    #register  new folders
    register_plugin_assets_directory(app, base_path="/plugins/bocx/admin/challenges/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/admin/settings/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/assets/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/assets/js/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/admin/assets/img/")
