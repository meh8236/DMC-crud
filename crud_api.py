from crud_db import get_db, Bird, init_db
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()
init_db()


class BirdCreate(BaseModel):
    name: str


class BirdUpdate(BaseModel):
    name: str


class BirdResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class Message(BaseModel):
    message: str


@app.post("/birds/", response_model=BirdResponse)
def create_bird(bird: BirdCreate, db: Session = Depends(get_db)):
    new_bird = Bird(name=bird.name)
    db.add(new_bird)
    db.commit()
    db.refresh(new_bird)
    return new_bird


@app.get("/birds/", response_model=list[BirdResponse])
def read_birds(db: Session = Depends(get_db)):
    birds = db.execute(select(Bird)).scalars().all()
    return birds


@app.get("/birds/{bird_id}", response_model=BirdResponse)
def read_bird(bird_id: int, db: Session = Depends(get_db)):
    query = select(Bird).where(Bird.id == bird_id)
    found_bird = db.execute(query).scalar_one()
    if found_bird is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bird not found")
    return found_bird


@app.put("/birds/{bird_id}", response_model=BirdResponse)
def update_bird(bird_id: int, bird: BirdUpdate, db: Session = Depends(get_db)):
    found_bird = read_bird(bird_id, db)
    found_bird.name = bird.name
    db.commit()
    db.refresh(found_bird)
    return found_bird


@app.delete("/birds/{bird_id}", response_model=Message)
def delete_bird(bird_id: int, db: Session = Depends(get_db)):
    found_bird = read_bird(bird_id, db)
    db.delete(found_bird)
    db.commit()
    return Message(message='Bird deleted successfully')

@app.put("/birds/{bird_1_id}/{bird_2_id}", response_model= Message)
def switch_bird(
        bird_1_id:int,
        bird_2_id:int,
        db: Session = Depends(get_db)):


    b1 = read_bird(bird_1_id, db)
    b1n=b1.name
    b2 = read_bird(bird_2_id, db)
    b2n=b2.name
    temp_id=0

    b1.name=b2n
    b2.name=b1n

    db.commit()
    return Message(message='Birds switched successfully')


def main():
    uvicorn.run(app)


if __name__ == '__main__':
    main()
