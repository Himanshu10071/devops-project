from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Member, Trainer
from ..schemas import TrainerCreate, TrainerOut, TrainerUpdate

router = APIRouter(prefix="/api/trainers", tags=["trainers"])


def _get_or_404(db: Session, trainer_id: int) -> Trainer:
    trainer = db.get(Trainer, trainer_id)
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return trainer


def _to_out(db: Session, trainer: Trainer) -> TrainerOut:
    count = db.scalar(select(func.count(Member.id)).where(Member.trainer_id == trainer.id)) or 0
    return TrainerOut.model_validate(trainer).model_copy(update={"member_count": count})


@router.get("", response_model=list[TrainerOut])
def list_trainers(db: Session = Depends(get_db)):
    counts = dict(
        db.execute(
            select(Member.trainer_id, func.count(Member.id)).where(Member.trainer_id.is_not(None)).group_by(Member.trainer_id)
        ).all()
    )
    trainers = db.scalars(select(Trainer).order_by(Trainer.name))
    return [TrainerOut.model_validate(t).model_copy(update={"member_count": counts.get(t.id, 0)}) for t in trainers]


@router.get("/{trainer_id}", response_model=TrainerOut)
def get_trainer(trainer_id: int, db: Session = Depends(get_db)):
    return _to_out(db, _get_or_404(db, trainer_id))


@router.post("", response_model=TrainerOut, status_code=status.HTTP_201_CREATED)
def create_trainer(payload: TrainerCreate, db: Session = Depends(get_db)):
    trainer = Trainer(**payload.model_dump())
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return _to_out(db, trainer)


@router.put("/{trainer_id}", response_model=TrainerOut)
def update_trainer(trainer_id: int, payload: TrainerUpdate, db: Session = Depends(get_db)):
    trainer = _get_or_404(db, trainer_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(trainer, key, value)
    db.commit()
    db.refresh(trainer)
    return _to_out(db, trainer)


@router.delete("/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trainer(trainer_id: int, db: Session = Depends(get_db)):
    trainer = _get_or_404(db, trainer_id)
    # Members keep their membership; they just lose the assigned trainer.
    db.execute(update(Member).where(Member.trainer_id == trainer_id).values(trainer_id=None))
    db.delete(trainer)
    db.commit()
