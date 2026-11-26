from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from models.leaderboard import LeaderboardEntry
from models.player_profile import PlayerProfile
from models.user import User


def recalculate_leaderboard(db: Session) -> None:
    """อัปเดตคะแนนของทุกคนในระบบและจัดอันดับ 1, 2, 3, ... ใหม่ทั้งหมด"""
    rows = db.execute(
        select(User.id, PlayerProfile.total_score)
        .join(PlayerProfile, PlayerProfile.user_id == User.id)
        .where(User.is_active.is_(True))
        .order_by(desc(PlayerProfile.total_score), PlayerProfile.updated_at.asc(), User.id.asc())
    ).all()

    existing_map = {
        entry.user_id: entry
        for entry in db.scalars(select(LeaderboardEntry)).all()
    }

    active_user_ids = set()
    for index, (user_id, total_score) in enumerate(rows, start=1):
        active_user_ids.add(user_id)
        entry = existing_map.get(user_id)
        if entry is None:
            db.add(
                LeaderboardEntry(
                    user_id=user_id,
                    rank=index,
                    total_score=total_score,
                )
            )
        else:
            entry.rank = index
            entry.total_score = total_score

    # ลบรายการของผู้ใช้ที่ไม่ได้ใช้งานแล้ว (ถ้ามี)
    for uid, entry in existing_map.items():
        if uid not in active_user_ids:
            db.delete(entry)

    db.flush()


def get_full_leaderboard(db: Session) -> dict:
    """ดึงตารางอันดับทั้งหมดหน้าเดียว (1 ถึงคนสุดท้าย)"""
    # ซิงก์ให้แน่ใจว่าผู้เล่นทุกคนมีอันดับล่าสุดเสมอ
    recalculate_leaderboard(db)
    db.commit()

    results = db.execute(
        select(
            LeaderboardEntry.rank,
            LeaderboardEntry.user_id,
            User.username,
            LeaderboardEntry.total_score,
            PlayerProfile.streak_count,
            LeaderboardEntry.updated_at,
        )
        .join(User, User.id == LeaderboardEntry.user_id)
        .join(PlayerProfile, PlayerProfile.user_id == User.id)
        .order_by(LeaderboardEntry.rank.asc())
    ).all()

    rankings = [
        {
            "rank": r.rank,
            "user_id": r.user_id,
            "username": r.username,
            "total_score": r.total_score,
            "streak_count": r.streak_count,
            "updated_at": r.updated_at,
        }
        for r in results
    ]

    return {
        "total_players": len(rankings),
        "rankings": rankings,
    }