from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest

from app import app, Food, db
 
@pytest.fixture(scope='module')
def test_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_delicious.sqlite3'
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='module')
def client(test_app):
    with test_app.test_client() as client:
        yield client


def test_show_all(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Show All Foods' in response.data


def test_new_food(client):
    response = client.post('/new', data={
        'name': 'Test Food',
        'price': 9.99,
        'availability': True
    })
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == 'http://localhost/'


def test_invalid_new_food(client):
    response = client.post('/new', data={
        'name': '',
        'price': 9.99,
        'availability': True
    })
    assert response.status_code == 200
    assert b'Please enter all the fields' in response.data


def test_update_food(client):
    food = Food(name='Initial Name', price=9.99, availability=True)
    db.session.add(food)
    db.session.commit()

    response = client.post(f'/update/{food.id}', data={
        'name': 'Updated Name',
        'price': 19.99,
        'availability': False
    })
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == 'http://localhost/'

    updated_food = Food.query.get(food.id)
    assert updated_food.name == 'Updated Name'
    assert updated_food.price == 19.99
    assert not updated_food.availability


def test_delete_food(client):
    food = Food(name='Food to Delete', price=9.99, availability=True)
    db.session.add(food)
    db.session.commit()

    response = client.get(f'/delete/{food.id}')
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == 'http://localhost/'

    deleted_food = Food.query.get(food.id)
    assert deleted_food is None
