from datetime import date, timedelta

from models.player_profile import PlayerProfile
from services.energy_service import get_bangkok_today


def update_daily_streak(
    profile: PlayerProfile, today: date | None = None
) -> PlayerProfile:
    """อัปเดตระบบเติมไฟรายวัน: ต่อเนื่อง +1, วันเดิมคงเดิม, ขาดช่วงเริ่มนับ 1 ใหม่"""
    current_day = today or get_bangkok_today()
    last_day = profile.last_streak_date

    if last_day == current_day:
        return profile

    if last_day is not None and (current_day - last_day) == timedelta(days=1):
        profile.streak_count += 1
    else:
        profile.streak_count = 1

    profile.last_streak_date = current_day
    if profile.streak_count > profile.best_streak:
        profile.best_streak = profile.streak_count

    return profile