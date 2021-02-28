def test_create_cuisine(db, cuisine_factory):
    cuisine = cuisine_factory.create()

    db.session.add(cuisine)
    db.session.commit()

    assert cuisine.time_updated is None
    assert cuisine.recipes == []
