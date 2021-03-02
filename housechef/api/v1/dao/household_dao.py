import datetime as dt

from flask import current_app
from sqlalchemy import and_

from housechef.database.models import Meal


class HouseholdDAO(object):
    @staticmethod
    def get_meals_for_day(household_id: int, date: dt.date = None):
        """Returns a list of meals for a given date that are associated with a houshold"""
        try:
            meals = Meal.query.filter(
                and_(Meal.household_id == household_id, Meal.date == date)
            ).all()
            return meals
        except Exception as e:
            current_app.logger.error(
                f"Error occurred while looking up meals for date {date.isoformat()}: {str(e)}"
            )
            return []
