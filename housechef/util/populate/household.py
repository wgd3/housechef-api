from faker import Faker

from housechef.database.models import Household, User

fake = Faker()


def create_and_populate_household(user_count=2):
    household = Household.create(name=fake.street_name())
    print(f"Created household '{household.name}'")
    for i in range(user_count):
        profile = fake.simple_profile()
        first_name: str = (
            fake.first_name_male()
            if profile["sex"] == "M"
            else fake.first_name_female()
        )
        last_name: str = profile["name"].split(" ").pop()
        username: str = f"{first_name[0].lower()}{last_name.lower()}"
        height = fake.pyint(min_value=59, max_value=76)
        bmi = fake.pyfloat(min_value=19, max_value=32)
        weight = (bmi / 703) * height * height

        user = User.create(
            username=username,
            email=f"{username}@{fake.free_email_domain()}",
            gender="male" if profile["sex"] == "M" else "female",
            birthday=fake.date_between(start_date="-60y", end_date="-21y"),
            first_name=first_name,
            last_name=last_name,
            password=fake.password(),
            household_id=household.id,
            height_inches=height,
            weight_lbs=weight,
            time_created=fake.date_between(start_date="-2y", end_date="-30d"),
        )
        print(
            f"\tAdded user {user.first_name} {user.last_name} ({user.age}, {user.gender}): {user.username} / {user.email} / {user.birthday} / {user.height_inches}in / {user.weight_lbs}lbs"
        )
