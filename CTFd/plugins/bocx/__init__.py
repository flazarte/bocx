import os
from flask import Blueprint
from CTFd.models import db, Challenges, Flags
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.plugins.challenges import BaseChallenge
from CTFd.plugins import override_template, register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.bocx.routing import bocx, bocx_static_html, bocx_view_challenge_category_api, bocx_view_challenge_category, bocx_chal_listing, get_CTF_name, get_bocx_team_name, bocx_challenges_listing, bocx_setting, bocx_category_update_api, bocx_challenges_new, bocx_challenges_detail, bocx_get_team_api, bocx_challenge_update_api 
from CTFd.plugins.bocx.models import CategoryGameClass





def load(app):
    app.db.create_all()
    app.register_blueprint(bocx)

    CHALLENGE_CLASSES["bocx_category"] = CategoryGameClass
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #override teemplates
    admin_challenges_list = os.path.join(dir_path, 'admin/challenges/challenges.html')
    override_template('admin/challenges/challenges.html', open(admin_challenges_list).read())
    #Challenges Override
    new_challenges = os.path.join(dir_path, 'templates/challenges.html')
    override_template('challenges.html', open(new_challenges).read())
    new_navbar = os.path.join(dir_path, 'templates/navbar.html')
    override_template('components/navbar.html', open(new_navbar).read())
    #admin_base
    new_base = os.path.join(dir_path, 'templates/neon-base.html')
    override_template('base.html', open(new_base).read())
    #admin_base = os.path.join(dir_path, 'admin/base.html')
    #override_template('admin/base.html', open(admin_base).read())
    #admin bocx setting
    app.view_functions['bocx.settings'] = bocx_setting
    app.add_url_rule('/api/v2/challenge-category/<int:bocx_id>', 'bocx.bocx_update_api',bocx_category_update_api)
    #user views
    app.view_functions['bocx.bocx_view_challenge_category'] = bocx_view_challenge_category
    #api routes
    app.view_functions['bocx.bocx_update_api'] = bocx_category_update_api
    app.view_functions['bocx.bocx_get_team_api'] = bocx_get_team_api
    app.view_functions['bocx.bocx_challenge_update_api'] = bocx_challenge_update_api
    app.view_functions['bocx.bocx_view_challenge_category_api'] = bocx_view_challenge_category_api
    #override routes
    app.view_functions['admin.challenges_new'] = bocx_challenges_new
    app.view_functions['admin.challenges_detail'] = bocx_challenges_detail
    app.view_functions['admin.challenges_listing'] = bocx_challenges_listing
    app.view_functions['challenges.listing'] =  bocx_chal_listing
    app.view_functions['views.static_html'] = bocx_static_html
    #jinja
    app.jinja_env.filters['get_CTF_name'] = get_CTF_name
    app.jinja_env.filters['get_bocx_team_name'] = get_bocx_team_name
    #register  new folders
    register_plugin_assets_directory(app, base_path="/plugins/bocx/admin/challenges/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/admin/settings/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/assets/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/assets/js/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/admin/assets/img/")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/templates")
    register_plugin_assets_directory(app, base_path="/plugins/bocx/templates/assets")
