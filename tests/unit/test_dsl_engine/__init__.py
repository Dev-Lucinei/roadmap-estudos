# roadmap-estudos/tests/unit/test_dsl_engine/__init__.py

VALID_DSL = {
    "version": "1.0",
    "name": "Test Flow",
    "steps": [
        {"id": "step-1", "type": "lesson", "params": {"topic": "Python"}},
        {
            "id": "step-2",
            "type": "quiz",
            "params": {"topic": "Python", "question_count": 5},
        },
    ],
}
