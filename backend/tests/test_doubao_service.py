from datetime import UTC, datetime
from types import SimpleNamespace

from app.core.config import Settings
from app.services.doubao import DoubaoService


def test_doubao_image_analysis_parses_json_response() -> None:
    settings = Settings(ark_api_key="test-api-key")
    service = DoubaoService(settings)
    service._chat = lambda **_: """
    {
      "analysis_text": "Completed one calculus application problem.",
      "knowledge_points": ["definite integral", "geometry application"],
      "mistakes": ["Solution steps are incomplete"],
      "suggestions": ["Review similar problem types"]
    }
    """

    result = service.analyze_problem_image(
        image_bytes=b"fake image",
        content_type="image/png",
        record=SimpleNamespace(subject="math", module="advanced_math", title="Integral application"),
    )

    assert result.status == "completed"
    assert result.analysis_text == "Completed one calculus application problem."
    assert result.knowledge_points == ["definite integral", "geometry application"]
    assert result.mistakes == ["Solution steps are incomplete"]
    assert result.suggestions == ["Review similar problem types"]


def test_doubao_daily_review_parses_json_response() -> None:
    settings = Settings(ark_api_key="test-api-key")
    service = DoubaoService(settings)
    service._chat = lambda **_: """
    {
      "summary": "Math and 408 both moved forward today.",
      "completed_content": "Integral applications; tree traversal mistakes",
      "weak_points": "Calculation steps and tree traversal edge cases",
      "next_actions": "Review mistakes first tomorrow, then drill similar problems"
    }
    """
    now = datetime.now(UTC)
    records = [
        SimpleNamespace(
            id=1,
            subject="math",
            module="advanced_math",
            title="Integral application",
            duration_minutes=60,
            summary="Finished one problem set",
        )
    ]

    result = service.generate_daily_review(review_date=now.date(), records=records, images=[])

    assert result.status == "completed"
    assert "Math" in result.summary
    assert "Integral" in result.completed_content
    assert "Review mistakes" in result.next_actions
