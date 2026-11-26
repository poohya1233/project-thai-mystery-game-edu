from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LeaderboardItemOut(BaseModel):
    rank: int
    user_id: int
    username: str
    total_score: int
    streak_count: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardListOut(BaseModel):
    total_players: int
    rankings: list[LeaderboardItemOut]