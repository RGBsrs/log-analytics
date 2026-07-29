from fastapi import APIRouter, Depends, status

from app.schemas.log_pattern import LogPatternRead
from app.services.pattern_service import PatternService, get_pattern_service

router = APIRouter(prefix="/analysis")


@router.post("/patterns", status_code=status.HTTP_202_ACCEPTED)
async def analyze(service: PatternService = Depends(get_pattern_service)):
    return await service.analyze(24)

@router.get("/patterns", response_model=list[LogPatternRead])
async def get_patterns(service: PatternService = Depends(get_pattern_service)):
    return await service.get_all()

@router.get("/patterns/new", response_model=list[LogPatternRead])
async def get_new_patterns(service: PatternService = Depends(get_pattern_service)):
    return await service.get_new()
