# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, List
import logging
import uuid

# ==== Logger Setup ====

# Input Logger
input_logger = logging.getLogger("input_logger")
input_logger.setLevel(logging.INFO)
input_handler = logging.FileHandler("input.log", mode="a")
input_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
input_logger.addHandler(input_handler)

# Output Logger
output_logger = logging.getLogger("output_logger")
output_logger.setLevel(logging.INFO)
output_handler = logging.FileHandler("output.log", mode="a")
output_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
output_logger.addHandler(output_handler)

# ==== FastAPI App ====

app = FastAPI()

# ==== Pydantic Models ====

class Qualification(BaseModel):
    exam: str = Field(..., description="Qualification exam: JEE or NEET")
    qualified: bool

    @validator("exam")
    def exam_must_be_known(cls, v):
        v = v.upper()
        if v not in {"JEE", "NEET", "NONE"}:
            raise ValueError("exam must be 'JEE', 'NEET', or 'None'")
        return v

class Student(BaseModel):
    name: str = Field(..., description="Student full name")
    age: int = Field(..., description="Age between 17 and 25")
    gender: str = Field(..., description="Male, Female, or Other")
    marks: Dict[str, float] = Field(
        ..., description="Map of subject → marks (0–100)"
    )
    qualification: Qualification
    desired_course: str = Field(..., description="One of the predefined courses")

    @validator("name")
    def name_letters_spaces(cls, v):
        import re
        if not re.fullmatch(r"[A-Za-z ]+", v):
            raise ValueError("Name should contain only letters and spaces")
        return v.strip()

    @validator("age")
    def age_range(cls, v):
        if not (17 <= v <= 25):
            raise ValueError("Age must be between 17 and 25")
        return v

    @validator("gender")
    def gender_values(cls, v):
        if v not in {"Male", "Female", "Other"}:
            raise ValueError("Gender must be 'Male', 'Female', or 'Other'")
        return v

    @validator("marks")
    def marks_range_and_count(cls, v):
        for subj, m in v.items():
            if not (0 <= m <= 100):
                raise ValueError(f"Marks for {subj} must be between 0 and 100")
        if len(v) < 3:
            raise ValueError("At least 3 subjects are required")
        return v

    @validator("desired_course")
    def course_must_be_defined(cls, v):
        valid = {
            "CSE","ME","EE","CIVIL","ECE",
            "MBBS","BDS","BAMS","BHMS","BPT",
            "BCOM","BBA","BBM","CA",
            "BA_HISTORY","BA_PSYCHOLOGY","BA_SOCIETY","BA_POLITICALSCI","BA_ENGLISH"
        }
        if v.upper() not in valid:
            raise ValueError(f"desired_course must be one of {sorted(valid)}")
        return v.upper()

# ==== Eligibility Logic & Cut‑offs ====

COURSE_RULES = {
    # course: (required subjects, cutoff %, required exam)
    "CSE":           ({"Physics","Chemistry","Mathematics"}, 75, "JEE"),
    "ME":            ({"Physics","Chemistry","Mathematics"}, 70, "JEE"),
    "EE":            ({"Physics","Chemistry","Mathematics"}, 70, "JEE"),
    "CIVIL":         ({"Physics","Chemistry","Mathematics"}, 65, "JEE"),
    "ECE":           ({"Physics","Chemistry","Mathematics"}, 70, "JEE"),
    "MBBS":          ({"Physics","Chemistry","Biology"},     85, "NEET"),
    "BDS":           ({"Physics","Chemistry","Biology"},     80, "NEET"),
    "BAMS":          ({"Physics","Chemistry","Biology"},     75, "NEET"),
    "BHMS":          ({"Physics","Chemistry","Biology"},     75, "NEET"),
    "BPT":           ({"Physics","Chemistry","Biology"},     70, "NEET"),
    "BCOM":          ({"Accountancy","Business Studies","Economics"}, 0, None),
    "BBA":           ({"Accountancy","Business Studies","Economics"}, 0, None),
    "BBM":           ({"Accountancy","Business Studies","Economics"}, 0, None),
    "CA":            ({"Accountancy","Business Studies","Economics"}, 0, None),
    "BA_HISTORY":    ({"History","Political Science","Geography"},    0, None),
    "BA_PSYCHOLOGY": ({"Psychology","Sociology","English"},           0, None),
    "BA_SOCIETY":    ({"Sociology","Political Science","History"},     0, None),
    "BA_POLITICALSCI":({"Political Science","History","Geography"},   0, None),
    "BA_ENGLISH":    ({"English","History","Political Science"},       0, None),
}

def calculate_percentage(marks: Dict[str, float]) -> float:
    """Compute simple average of all subjects."""
    return sum(marks.values()) / len(marks)

def check_course_eligibility(student: Student):
    course = student.desired_course
    rule = COURSE_RULES[course]
    req_subjs, cutoff, req_exam = rule

    # 1) exam check
    if req_exam:
        if student.qualification.exam != req_exam or not student.qualification.qualified:
            return False

    # 2) subject check
    if not req_subjs.issubset(set(student.marks.keys())):
        return False

    # 3) cutoff check
    pct = calculate_percentage({s: student.marks[s] for s in req_subjs})
    if cutoff > 0 and pct < cutoff:
        return False

    return True

def recommend_alternatives(student: Student) -> List[str]:
    recs = []
    for crs, (subjs, cutoff, req_exam) in COURSE_RULES.items():
        # exam
        if req_exam and (student.qualification.exam != req_exam or not student.qualification.qualified):
            continue
        # subjects
        if not subjs.issubset(set(student.marks.keys())):
            continue
        # cutoff
        pct = calculate_percentage({s: student.marks[s] for s in subjs})
        if cutoff > 0 and pct < cutoff:
            continue
        recs.append(crs)
    return recs

# ==== API Endpoint ====

@app.post("/check-eligibility")
async def check_eligibility(student: Student):
    # 1) log input
    input_logger.info(student.json())
    input_logger.handlers[0].flush()

    # 2) compute overall percentage
    overall_pct = calculate_percentage(student.marks)

    # 3) eligibility
    eligible = check_course_eligibility(student)

    # 4) recommendations if needed
    recommended = None
    if not eligible:
        recommended = recommend_alternatives(student)

    # 5) build response
    response = {
        "student_id": str(uuid.uuid4()),
        "eligible": eligible,
        "percentage": round(overall_pct, 2),
    }
    if recommended is not None:
        response["recommended_courses"] = recommended

    # 6) log output
    output_logger.info(response)
    output_logger.handlers[0].flush()

    return response

# ==== Global Error Handler ====

@app.exception_handler(Exception)
async def global_exception(request, exc):
    raise HTTPException(status_code=400, detail=str(exc))
