import os
from CTFd.models import db, Challenges, Flags
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.plugins.challenges import BaseChallenge

class Avatars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.Integer)
    location = db.Column(db.Text)

    def __init__(self, team, location):
        self.target = team
        self.location = location

class BOCX_category(db.Model):
    __tablename__ = 'bocx_category'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80))  
    description = db.Column(db.Text)
    team = db.Column(db.Integer) 
    image_name = db.Column(db.Text)
    location = db.Column(db.Text)
    
    def __init__(self, *args, **kwargs):
        super(BOCX_category, self).__init__(**kwargs)


class BOCX_lockout(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ctf_category_id = db.Column(
        db.Integer, db.ForeignKey("bocx_category.id", ondelete="CASCADE")
    )
    lockout_percentage = db.Column(db.Integer)
    def __init__(self, *args, **kwargs):
        super(BOCX_lockout, self).__init__(**kwargs)

class BOCX_selected_cat(db.Model):
    __tablename__ = 'bocx_selected_cat'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    ctf_category_id = db.Column(
        db.Integer, db.ForeignKey("bocx_category.id", ondelete="CASCADE")
    )
    team_id = db.Column(
        db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE")
    ) 
    def __init__(self, *args, **kwargs):
        super(BOCX_selected_cat, self).__init__(**kwargs)


class BOCXCategoryChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'bocx_category'}
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('challenges.id', ondelete="CASCADE"), primary_key=True)
    ctf_category_id = db.Column(
        db.Integer, db.ForeignKey("bocx_category.id", ondelete="CASCADE")
    )
    team_id = db.Column(
        db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE")
    )
    initial = db.Column(db.Integer)
    writeups = db.Column(db.Text)

    def __init__(self, ctf_category_id, team_id,  name, description, value, category,  writeups, type='bocx_category'):
        self.ctf_category_id = ctf_category_id
        self.team_id = team_id
        self.name = name
        self.description = description
        self.value = value
        self.initial = value
        self.category = category
        self.type = type
        self.writeups = writeups


class CategoryGameClass(BaseChallenge):
    id = "bocx_category"
    name = "bocx_category"

    templates = {
        "create": "/plugins/bocx/admin/challenges/create.html",
        "update": "/plugins/bocx/admin/challenges/update.html",
        "view": "/plugins/bocx/admin/challenges/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/bocx/admin/challenges/create.js",
        "update": "/plugins/bocx/admin/challenges/update.js",
        "view": "/plugins/bocx/admin/challenges/view.js",
    }
    #route = "/plugins/bocx/challenges/"
    # Blueprint used to access the static_folder directory.
    #blueprint = Blueprint(
     #   "bocx",
      #  __name__,
       # template_folder="templates",
       # static_folder="assets",
    #)
    challenge_model = BOCXCategoryChallenge

    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.
        :param request:
        :return:
        """
        # Create challenge
        data = request.form or request.get_json()
        chal = BOCXCategoryChallenge(
            ctf_category_id=data['bocx_category'],
            team_id=data['team_id'],
            name=data['name'],
            description=data['description'],
            value=data['value'],
            category=data['category'],
            type=data['type'],
            writeups=data['writeups']
        )

        db.session.add(chal)
        db.session.commit()

        return chal
    
    @classmethod
    def attempt(cls, challenge, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            try:
                if get_flag_class(flag.type).compare(flag, submission):
                    return True, "Correct"
            except FlagException as e:
                return False, str(e)
        return False, "Incorrect"
