from datetime import date, datetime
from zoneinfo import ZoneInfo

from models.player_profile import PlayerProfile

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


class InsufficientEnergyError(Exception):
    """เกิดเมื่อพลังงานชีวิตไม่พอสำหรับตอบคำถาม"""


class DailyQuestionLimitError(Exception):
    """เกิดเมื่อตอบคำถามครบโควตาสูงสุดต่อวันที่กำหนดไว้"""


def get_bangkok_today() -> date:
    return datetime.now(BANGKOK_TZ).date()


def sync_daily_energy(profile: PlayerProfile, today: date | None = None) -> PlayerProfile:
    """รีเซ็ตตัวนับรายวันและเติมพลังงานกลับเต็ม max_energy เมื่อเข้าวันใหม่"""
    current_day = today or get_bangkok_today()
    if profile.energy_reset_date != current_day:
        profile.energy = profile.max_energy
        profile.daily_questions_answered = 0
        profile.energy_reset_date = current_day
    return profile


def consume_energy_for_answer(
    profile: PlayerProfile, today: date | None = None
) -> PlayerProfile:
    """หักพลังงานทุกครั้งที่ตอบคำถาม (ไม่ว่าจะถูกหรือผิด) พร้อมตรวจโควตารายวัน"""
    sync_daily_energy(profile, today=today)

    if (
        profile.daily_question_limit is not None
        and profile.daily_questions_answered >= profile.daily_question_limit
    ):
        raise DailyQuestionLimitError("Daily question limit reached")

    cost = max(0, profile.energy_cost_per_answer)
    if profile.energy < cost:
        raise InsufficientEnergyError("Not enough energy to answer question")

    profile.energy -= cost
    profile.daily_questions_answered += 1
    return profile