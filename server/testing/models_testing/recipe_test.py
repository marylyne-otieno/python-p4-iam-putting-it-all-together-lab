import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User  # ✅ Make sure User is imported too

class TestRecipe:
    '''Recipe in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="TestUser")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" +
                    """ raptures building an bringing be. Elderly is detract""" +
                    """ tedious assured private so to visited. Do travelling""" +
                    """ companions contrasted it. Mistress strongly remember""" +
                    """ up to. Ham him compass you proceed calling detract.""" +
                    """ Better of always missed we person mr. September""" +
                    """ smallness northward situation few her certainty""" +
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id  # ✅ Assign a valid user_id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert "Ham him compass" in new_recipe.instructions
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id  # ✅ Ensure it's linked

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="AnotherUser")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                instructions="This is a long instruction string for validation to pass.",
                minutes_to_complete=30,
                user_id=user.id
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''raises error for instructions < 50 characters'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="ThirdUser")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="Too short",
                    minutes_to_complete=30,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()
