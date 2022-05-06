from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from . import crud, models, shemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/items/', response_model=list[shemas.Item], tags=['Items'])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.get('/users/', response_model=list[shemas.User], tags=['Users'])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get('/users/{user_id}', response_model=shemas.User, tags=['Users'])
def read_user(
        user_id: int = Path(..., title='The ID of the user to get'),
        db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


@app.post('/users/', response_model=shemas.User, tags=['Users'])
def create_user(user: shemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    return crud.create_user(db=db, user=user)


@app.post('/users/{user_id}/items/', response_model=shemas.Item,
          tags=['Items'])
def create_item_for_user(
        user_id: int, item: shemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)
