"""
Seed data — populates the database with initial companies, users, assessments,
and questions so the platform is usable immediately after `python init_db.py`.
"""
from __future__ import annotations

import logging

from app.api.security import hash_password
from app.database import SessionLocal
from app.models import Assessment, Company, Question, Skill, User, UserSkill

logger = logging.getLogger("backend.seed")


def seed_database(db=None):
    if db is None:
        db = SessionLocal()

    try:
        # --- Companies ---
        if db.query(Company).count() == 0:
            comp = Company(name="TechCorp")
            db.add(comp)
            db.commit()
            db.refresh(comp)
        else:
            comp = db.query(Company).first()

        # --- Questions: Backend Engineer Assessment ---
        bqa_questions = [
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="Which HTTP status code indicates a successful resource creation?",
                options=["200 OK", "201 Created", "204 No Content", "302 Found"],
                correct_options=[1],
                difficulty=0.2,
                skills="Backend,HTTP",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="In PostgreSQL, which command creates an index?",
                options=["MAKE INDEX", "CREATE INDEX", "ADD INDEX", "NEW INDEX"],
                correct_options=[1],
                difficulty=0.3,
                skills="SQL",
                language="sql",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="Which of the following best describes idempotency in REST APIs?",
                options=["Response is cached", "Multiple identical requests have the same effect as one", "Request always returns 200", "Request cannot be repeated"],
                correct_options=[1],
                difficulty=0.35,
                skills="Backend,HTTP",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="What is the time complexity of a binary search on a sorted array?",
                options=["O(n)", "O(log n)", "O(n log n)", "O(1)"],
                correct_options=[1],
                difficulty=0.4,
                skills="Algorithms",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="Which data structure is used to implement a priority queue?",
                options=["Stack", "Queue", "Min-Heap", "Hash Table"],
                correct_options=[2],
                difficulty=0.45,
                skills="Algorithms,Data Structures",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="sql",
                prompt="Write a query to select all users who signed up in the last 7 days.",
                options=[],
                correct_options=[],
                difficulty=0.5,
                skills="SQL",
                language="sql",
                starter_code="SELECT * FROM users\nWHERE ",
                test_cases_template=[
                    {"name": "recent_users_included", "passed": True, "hidden": False},
                    {"name": "users_8_days_excluded", "passed": True, "hidden": False},
                ],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="coding",
                prompt="Implement a function that returns the two indices of numbers in an array that add up to a target value.",
                options=[],
                correct_options=[],
                difficulty=0.6,
                skills="Algorithms,Python",
                language="python",
                starter_code="def two_sum(nums, target):\n    # your code here\n    pass",
                test_cases_template=[
                    {"name": "basic_case", "passed": True, "hidden": False},
                    {"name": "negative_numbers", "passed": True, "hidden": True},
                    {"name": "no_solution", "passed": True, "hidden": True},
                ],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="Which layer of the OSI model does TCP belong to?",
                options=["Transport", "Network", "Session", "Presentation"],
                correct_options=[0],
                difficulty=0.55,
                skills="Networking",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="short_answer",
                prompt="Explain the difference between INNER JOIN and LEFT JOIN.",
                options=[],
                correct_options=[],
                difficulty=0.65,
                skills="SQL",
                language="sql",
                starter_code="",
                test_cases_template=[],
                rubric=[
                    "Defines INNER JOIN correctly (returns only matching rows)",
                    "Defines LEFT JOIN correctly (returns all left rows + matching right)",
                    "Provides a practical example or use case",
                ],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="In microservices architecture, what is the purpose of a circuit breaker?",
                options=["Encrypt network traffic", "Prevent cascading failures", "Load balance requests", "Cache responses"],
                correct_options=[1],
                difficulty=0.7,
                skills="System Design",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
        ]

        # --- Questions: Python Skill Assessment ---
        psa_questions = [
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="What is the output of: list(map(lambda x: x*2, [1, 2, 3]))?",
                options=["[1, 2, 3]", "[2, 4, 6]", "[1, 4, 9]", "Error"],
                correct_options=[1],
                difficulty=0.25,
                skills="Python",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="Which of these is NOT a valid Python data structure?",
                options=["List", "Tuple", "Dictionary", "Array"],
                correct_options=[3],
                difficulty=0.3,
                skills="Python",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="coding",
                prompt="Find the first non-repeating character in a string.",
                options=[],
                correct_options=[],
                difficulty=0.55,
                skills="Algorithms,Python",
                language="python",
                starter_code="def first_non_repeating_char(s):\n    # your code here\n    pass",
                test_cases_template=[
                    {"name": "basic_case", "passed": True, "hidden": False},
                    {"name": "all_repeating", "passed": True, "hidden": True},
                ],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="What does the 'with' statement do in Python?",
                options=["Creates a new context", "Acts as a context manager protocol wrapper", "Imports a module", "Defines a class"],
                correct_options=[1],
                difficulty=0.45,
                skills="Python",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="Which decorator ensures a method can only be called once an instance is created?",
                options=["@property", "@staticmethod", "@classmethod", "@cached_property"],
                correct_options=[2],
                difficulty=0.5,
                skills="Python",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
        ]

        # --- Questions: System Design Assessment ---
        sda_questions = [
            Question(
                assessment_id=None,
                question_type="system_design",
                prompt="Design a URL shortener service.",
                options=[],
                correct_options=[],
                difficulty=0.8,
                skills="System Design",
                language="python",
                starter_code="",
                test_cases_template=[],
                rubric=[
                    "API design (endpoint, request/response format)",
                    "Data model / storage approach",
                    "Scalability and bottleneck handling (hashing, DB sharding)",
                    "Short URL uniqueness and collision resistance",
                    "Expiration / cleanup strategy",
                ],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="What is the primary benefit of using a CDN?",
                options=["Encrypts data in transit", "Reduces server-side computation", "Caches content closer to users", "Manages database connections"],
                correct_options=[2],
                difficulty=0.35,
                skills="System Design",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
            Question(
                assessment_id=None,
                question_type="mcq",
                prompt="In a database, what does ACID stand for?",
                options=[
                    "Atomic, Consistent, Isolated, Durable",
                    "Atomic, Centralized, Indexed, Distributed",
                    "Asynchronous, Consistent, Indexed, Durable",
                    "Atomic, Cached, Isolated, Distributed",
                ],
                correct_options=[0],
                difficulty=0.4,
                skills="SQL",
                language="python",
                test_cases_template=[],
                rubric=[],
                is_public=True,
            ),
        ]

        assessments = [
            {
                "title": "Backend Engineer Assessment",
                "description": "Core backend engineering: HTTP, SQL, algorithms, system design.",
                "company_id": comp.id,
                "duration_minutes": 90,
                "total_questions": len(bqa_questions),
                "skills": ["Backend", "SQL", "Algorithms", "System Design"],
                "difficulty_distribution": {"easy": 3, "medium": 4, "hard": 3},
                "allowed_question_types": "mcq,multi_select,coding,sql,short_answer,system_design",
                "coding_languages": "python,sql",
                "is_adaptive": True,
                 "scoring_rubric": {
                    "dimensions": {"Backend": 0.3, "SQL": 0.25, "Algorithms": 0.25, "System Design": 0.2},
                    "passing_score": 60,
                },
                "questions": bqa_questions,
            },
            {
                "title": "Python Skill Assessment",
                "description": "Python fundamentals and algorithmic problem solving.",
                "company_id": None,
                "duration_minutes": 45,
                "total_questions": len(psa_questions),
                "skills": ["Python", "Algorithms"],
                "difficulty_distribution": {"easy": 3, "medium": 2},
                "allowed_question_types": "mcq,coding",
                "coding_languages": "python",
                "is_adaptive": True,
                 "scoring_rubric": {
                    "dimensions": {"Python": 0.6, "Algorithms": 0.4},
                    "passing_score": 65,
                },
                "questions": psa_questions,
            },
            {
                "title": "System Design Assessment",
                "description": "Fundamental system design and architecture principles.",
                "company_id": None,
                "duration_minutes": 60,
                "total_questions": len(sda_questions),
                "skills": ["System Design", "SQL"],
                "difficulty_distribution": {"easy": 2, "medium": 0, "hard": 1},
                "allowed_question_types": "mcq,system_design",
                "coding_languages": "",
                "is_adaptive": True,
                 "scoring_rubric": {
                    "dimensions": {"System Design": 0.6, "SQL": 0.4},
                    "passing_score": 70,
                },
                "questions": sda_questions,
            },
        ]

        for a_data in assessments:
            existing = db.query(Assessment).filter(Assessment.title == a_data["title"]).first()
            if existing:
                continue
            a = Assessment(
                title=a_data["title"],
                description=a_data["description"],
                company_id=a_data["company_id"],
                duration_minutes=a_data["duration_minutes"],
                total_questions=a_data["total_questions"],
                skills=",".join(a_data["skills"]),
                difficulty_distribution=a_data["difficulty_distribution"],
                allowed_question_types=a_data["allowed_question_types"],
                coding_languages=a_data["coding_languages"],
                is_adaptive=a_data["is_adaptive"],
                scoring_rubric=a_data["scoring_rubric"],
                is_active=True,
            )
            db.add(a)
            db.commit()
            db.refresh(a)

            for q_obj in a_data["questions"]:
                q_obj.assessment_id = a.id
                db.add(q_obj)
            db.commit()

            logger.info("Seeded assessment '%s' with %d questions", a.title, len(a_data["questions"]))

        # --- Users ---
        # Trainer
        trainer_email = "trainer@techcorp.io"
        if not db.query(User).filter(User.email == trainer_email).first():
            t = User(
                email=trainer_email,
                password_hash=hash_password("trainer123"),
                full_name="Sarah Mehta",
                role="trainer",
                company_id=comp.id,
            )
            db.add(t)

        # Admin
        admin_email = "admin@techcorp.io"
        if not db.query(User).filter(User.email == admin_email).first():
            a_user = User(
                email=admin_email,
                password_hash=hash_password("admin123"),
                full_name="Arjun Shah",
                role="admin",
                company_id=comp.id,
            )
            db.add(a_user)

        # Candidate
        cand_email = "candidate@skillgraph.dev"
        if not db.query(User).filter(User.email == cand_email).first():
            c = User(
                email=cand_email,
                password_hash=hash_password("candidate123"),
                full_name="Rudrant Joshi",
                role="candidate",
                company_id=comp.id,
            )
            db.add(c)

        # Demo candidate (email from frontend)
        demo_email = "rudrant@demo.dev"
        if not db.query(User).filter(User.email == demo_email).first():
            d = User(
                email=demo_email,
                password_hash=hash_password("demo123"),
                full_name="Rudrant Joshi",
                role="candidate",
                company_id=None,
            )
            db.add(d)

        db.commit()

        # --- Skills ---
        predefined_skills = [
            ("Python", "lang"), ("React", "fw"), ("FastAPI", "fw"),
            ("SQL", "db"), ("Docker", "tool"), ("Testing", "concept"),
            ("System Design", "concept"), ("Algorithms", "concept"),
            ("Backend", "concept"), ("Networking", "concept"),
            ("HTTP", "concept"), ("Data Structures", "concept"),
            ("Git", "tool"), ("Redis", "tool"),
        ]
        for name, cat in predefined_skills:
            if not db.query(Skill).filter(Skill.name == name).first():
                db.add(Skill(name=name, category=cat))
        db.commit()

        logger.info("Seed data complete. Users, skills, and assessments loaded.")

    finally:
        if db is None or db.bind is not None:
            pass


def create_initial_data(db=None):
    """Public alias for seed_database."""
    return seed_database(db)
