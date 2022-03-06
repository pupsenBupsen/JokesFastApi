from enum import unique
import imp
import sqlite3
from sys import modules
from aiohttp import request
from fastapi import FastAPI
from pydantic import BaseModel

from tortoise import fields
from tortoise.models import Model 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

app = FastAPI()

class Jokes(Model):
    id = fields.IntField(pk = True)
    text = fields.CharField(200, unique = True)

Jokes_Pydantic = pydantic_model_creator(Jokes, name = 'Jokes')
JokesIn_Pydantic = pydantic_model_creator(Jokes, name = 'JokesIn', exclude_readonly = True)

@app.get('/')
def index():
    return{'key' : 'value'}

@app.get('/jokes')
async def get_AllJokes():
    return await Jokes_Pydantic.from_queryset(Jokes.all())

@app.get('/jokes/{jokes_id}')
async def get_jokes(jokes_id: int):
    return await Jokes_Pydantic.from_queryset_single(Jokes.get(id = jokes_id))

@app.post('/jokes')
async def create_jokes(jokes: JokesIn_Pydantic):
    jokes_obj = await Jokes.create(**jokes.dict(exclude_unset = True))
    return await Jokes_Pydantic.from_tortoise_orm(jokes_obj)

@app.delete('/jokes/{jokes_id}')
async def delete_jokes(jokes_id: int):
    await  Jokes.filter(id = jokes_id).delete()
    return{}

register_tortoise(
    app,
    db_url = 'sqlite://db.sqlite3',
    modules = {'models': ['main']},
    generate_schemas = True,
    add_exception_handlers = True
)