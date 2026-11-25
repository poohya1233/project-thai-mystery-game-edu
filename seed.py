from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database.base import Base
from database.connection import SessionLocal, engine
from models.game.chapter import Chapter
from models.game.question import Question
from models.game.stage import Stage


SEED_CHAPTERS = [
    {
        "chapter_number": 1,
        "title": "พยางค์และคำ",
        "description": "แยกแยะพยางค์เปิด-พยางค์ปิด และโครงสร้างคำไทยท่ามกลางม่านหมอกแรก",
        "intro_3d_scene_key": "ch01_fog_gate_intro",
        "intro_3d_duration_sec": 12,
        "stages": [
            {
                "stage_number": 1,
                "title": "เสียงก้องในหมอก",
                "instruction": "นับจำนวนพยางค์ของคำที่ปรากฏให้ถูกต้อง",
                "reward_score": 50,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "คำว่า \"ผจญภัย\" มีกี่พยางค์",
                        "choices": ["2 พยางค์", "3 พยางค์", "4 พยางค์", "5 พยางค์"],
                        "correct_answer": "3 พยางค์",
                        "explanation": "ผะ-จอน-ไพ รวมเป็น 3 พยางค์",
                        "points": 10,
                    },
                    {
                        "order_index": 2,
                        "prompt": "คำใดมี 2 พยางค์",
                        "choices": ["ศิลา", "อักขรา", "พิชิตหมอก", "ผจญภัย"],
                        "correct_answer": "ศิลา",
                        "explanation": "ศิ-ลา มี 2 พยางค์",
                        "points": 10,
                    },
                ],
            },
            {
                "stage_number": 2,
                "title": "พยางค์เปิดและพยางค์ปิด",
                "instruction": "สังเกตตัวสะกดเพื่อจำแนกพยางค์ปิด",
                "reward_score": 60,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "คำใดเป็นพยางค์ปิดทั้งหมด",
                        "choices": ["ม้า", "นก", "ปู", "ตา"],
                        "correct_answer": "นก",
                        "explanation": "\"นก\" มี ก เป็นตัวสะกด จึงเป็นพยางค์ปิด",
                        "points": 15,
                    },
                ],
            },
        ],
    },
    {
        "chapter_number": 2,
        "title": "มาตราตัวสะกด",
        "description": "ไขรหัสแม่กง แม่กน แม่กม แม่กก แม่กด แม่กบ แม่กนก และแม่เกย",
        "intro_3d_scene_key": "ch02_rune_pillars_intro",
        "intro_3d_duration_sec": 14,
        "stages": [
            {
                "stage_number": 1,
                "title": "เสาหลักแม่กงและแม่กน",
                "instruction": "เลือกคำที่สะกดตรงตามมาตราที่กำหนด",
                "reward_score": 50,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "คำว่า \"แสงสว่าง\" อยู่ในมาตราตัวสะกดใด",
                        "choices": ["แม่กง", "แม่กน", "แม่กม", "แม่กก"],
                        "correct_answer": "แม่กง",
                        "explanation": "ง เป็นตัวสะกดในมาตราแม่กง",
                        "points": 10,
                    },
                ],
            },
            {
                "stage_number": 2,
                "title": "เงาในแม่กดและแม่กบ",
                "instruction": "ระวังตัวสะกดไม่ตรงมาตรา",
                "reward_score": 60,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "คำใดอยู่ในมาตราแม่กด",
                        "choices": ["ภาพ", "ชาติ", "เมฆ", "สุข"],
                        "correct_answer": "ชาติ",
                        "explanation": "\"ชาติ\" อ่านออกเสียงเหมือนมี ด สะกด (มาตราแม่กด)",
                        "points": 15,
                    },
                ],
            },
        ],
    },
    {
        "chapter_number": 3,
        "title": "การผันอักษร",
        "description": "ผสานเสียงวรรณยุกต์กับอักษรสูง กลาง และต่ำเพื่อเปิดทางผ่าน",
        "intro_3d_scene_key": "ch03_tone_chimes_intro",
        "intro_3d_duration_sec": 13,
        "stages": [
            {
                "stage_number": 1,
                "title": "ระฆังเสียงวรรณยุกต์",
                "instruction": "ระบุระดับเสียงวรรณยุกต์ของคำ",
                "reward_score": 50,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "คำว่า \"น้ำ\" มีเสียงวรรณยุกต์ใด",
                        "choices": ["สามัญ", "เอก", "โท", "ตรี"],
                        "correct_answer": "ตรี",
                        "explanation": "\"น้ำ\" เป็นอักษรต่ำ (น) ผสมสระอำ และรูปวรรณยุกต์โท ออกเสียงตรี",
                        "points": 10,
                    },
                ],
            },
            {
                "stage_number": 2,
                "title": "อักษรสามหมู่พิทักษ์คำ",
                "instruction": "ตรวจสอบหมู่อักษรเริ่มต้นของคำ",
                "reward_score": 60,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "พยัญชนะ \"ข\" จัดอยู่ในอักษรหมู่ใด",
                        "choices": ["อักษรสูง", "อักษรกลาง", "อักษรต่ำ", "ไม่มีข้อถูก"],
                        "correct_answer": "อักษรสูง",
                        "explanation": "ข อยู่ในกลุ่มอักษรสูง (ผี ฝาก ถุง ข้าว สาร ให้ ฉัน)",
                        "points": 15,
                    },
                ],
            },
        ],
    },
    {
        "chapter_number": 4,
        "title": "ชนิดคำ",
        "description": "จำแนกคำนาม คำสรรพนาม คำกริยา และคำวิเศษณ์ในหอคอยปริศนา",
        "intro_3d_scene_key": "ch04_word_archive_intro",
        "intro_3d_duration_sec": 15,
        "stages": [
            {
                "stage_number": 1,
                "title": "ศิลาคำนามและคำกริยา",
                "instruction": "แยกหน้าที่ของคำในบริบทสั้น ๆ",
                "reward_score": 50,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "ในประโยค \"หมอกหนาปกคลุมหุบเขา\" คำว่า \"ปกคลุม\" เป็นคำชนิดใด",
                        "choices": ["คำนาม", "คำสรรพนาม", "คำกริยา", "คำวิเศษณ์"],
                        "correct_answer": "คำกริยา",
                        "explanation": "\"ปกคลุม\" แสดงอาการหรือการกระทำ จึงเป็นคำกริยา",
                        "points": 10,
                    },
                ],
            },
            {
                "stage_number": 2,
                "title": "คำวิเศษณ์ขยายความ",
                "instruction": "หาคำที่ทำหน้าที่ขยายความหมาย",
                "reward_score": 60,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "ในประโยค \"นักผจญภัยเดินอย่างระมัดระวัง\" คำใดเป็นคำวิเศษณ์",
                        "choices": ["นักผจญภัย", "เดิน", "อย่างระมัดระวัง", "ไม่มี"],
                        "correct_answer": "อย่างระมัดระวัง",
                        "explanation": "\"อย่างระมัดระวัง\" ขยายกริยา \"เดิน\"",
                        "points": 15,
                    },
                ],
            },
        ],
    },
    {
        "chapter_number": 5,
        "title": "ประโยค",
        "description": "เรียงร้อยใจความสำคัญและโครงสร้างประโยคเพื่อสลายหมอกสุดท้าย",
        "intro_3d_scene_key": "ch05_sanctum_dawn_intro",
        "intro_3d_duration_sec": 16,
        "stages": [
            {
                "stage_number": 1,
                "title": "ภาคประธานและภาคแสดง",
                "instruction": "ระบุส่วนประกอบหลักของประโยค",
                "reward_score": 60,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "ในประโยค \"แสงอรุณสาดส่องยอดเขา\" ส่วนใดคือภาคประธาน",
                        "choices": ["แสงอรุณ", "สาดส่อง", "ยอดเขา", "สาดส่องยอดเขา"],
                        "correct_answer": "แสงอรุณ",
                        "explanation": "\"แสงอรุณ\" เป็นผู้ถูกกระทำ/ผู้กระทำหลักของประโยค (ภาคประธาน)",
                        "points": 15,
                    },
                ],
            },
            {
                "stage_number": 2,
                "title": "ชนิดของประโยคเพื่อสื่อสาร",
                "instruction": "เลือกชนิดประโยคให้ตรงกับเจตนา",
                "reward_score": 70,
                "questions": [
                    {
                        "order_index": 1,
                        "prompt": "ประโยค \"จงไขปริศนาแห่งอักขราให้สำเร็จ\" เป็นประโยคชนิดใด",
                        "choices": ["ประโยคบอกเล่า", "ประโยคคำถาม", "ประโยคคำสั่ง", "ประโยคขอร้อง"],
                        "correct_answer": "ประโยคคำสั่ง",
                        "explanation": "มีคำว่า \"จง\" แสดงการสั่งหรือกำชับให้กระทำ",
                        "points": 20,
                    },
                ],
            },
        ],
    },
]


def seed_database(db: Session) -> dict[str, int]:
    chapters_created = 0
    stages_created = 0
    questions_created = 0

    for ch_data in SEED_CHAPTERS:
        chapter = db.scalar(
            select(Chapter).where(Chapter.chapter_number == ch_data["chapter_number"])
        )
        if chapter is None:
            chapter = Chapter(
                chapter_number=ch_data["chapter_number"],
                title=ch_data["title"],
                description=ch_data["description"],
                intro_3d_scene_key=ch_data["intro_3d_scene_key"],
                intro_3d_duration_sec=ch_data["intro_3d_duration_sec"],
                is_active=True,
            )
            db.add(chapter)
            db.flush()
            chapters_created += 1

        for st_data in ch_data["stages"]:
            stage = db.scalar(
                select(Stage).where(
                    Stage.chapter_id == chapter.id,
                    Stage.stage_number == st_data["stage_number"],
                )
            )
            if stage is None:
                stage = Stage(
                    chapter_id=chapter.id,
                    stage_number=st_data["stage_number"],
                    title=st_data["title"],
                    instruction=st_data["instruction"],
                    reward_score=st_data["reward_score"],
                    is_active=True,
                )
                db.add(stage)
                db.flush()
                stages_created += 1

            for q_data in st_data["questions"]:
                question = db.scalar(
                    select(Question).where(
                        Question.stage_id == stage.id,
                        Question.order_index == q_data["order_index"],
                    )
                )
                if question is None:
                    question = Question(
                        stage_id=stage.id,
                        order_index=q_data["order_index"],
                        prompt=q_data["prompt"],
                        choices=q_data["choices"],
                        correct_answer=q_data["correct_answer"],
                        explanation=q_data["explanation"],
                        points=q_data["points"],
                    )
                    db.add(question)
                    questions_created += 1

    db.commit()
    return {
        "chapters_created": chapters_created,
        "stages_created": stages_created,
        "questions_created": questions_created,
    }


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        summary = seed_database(db)
    print("Seed completed:", summary)


if __name__ == "__main__":
    main()