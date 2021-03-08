from faker import Faker

from housechef.database.models import Household, User, Role

fake = Faker()


def create_base_users():
    household = Household.create(name=fake.street_name())

    test_user = User.create(
        username="testuser",
        email="noreply@housechef.io",
        password="testuser",
        gender="male",
        birthday=fake.date_between(start_date="-40y", end_date="-21y"),
        first_name="test",
        last_name="user",
        household_id=household.id,
    )

    admin_user = User.create(
        username="admin",
        password="admin",
        email="admin@housechef.io",
        gender="male",
        birthday=fake.date_between(start_date="-40y", end_date="-21y"),
        first_name="admin",
        last_name="user",
        household_id=household.id,
    )
    admin_role = Role.query.filter(Role.name == "Admin").one_or_none()
    if admin_role is not None:
        admin_user.roles.append(admin_role)
        admin_user.save()
    else:
        print(f"Warning - no Admin role detected! Admin user only has the User role")
    print(f"Successfully created 'testuser' and 'admin' in house '{household.name}'")
