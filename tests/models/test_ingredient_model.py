def test_create_ingredient(db, ingredient_factory):
    i = ingredient_factory.create()

    db.session.add(i)
    db.session.commit()

    assert i.time_updated is None
    assert i.recipes == []
