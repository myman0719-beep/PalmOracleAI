from analysis_engine import analyze_personality
from career_engine import suggest_career
from summary_engine import create_summary


def generate_report(scores):
    report = []
    analysis = analyze_personality(scores)
    careers = suggest_career(scores)
    summary = create_summary(scores)

    report.append("=" * 50)
    report.append("KẾT QUẢ PHÂN TÍCH CHỈ TAY")
    report.append("=" * 50)
    report.append("")

    report.append("=" * 50)
    report.append("PHÂN TÍCH TÍNH CÁCH")
    report.append("=" * 50)
    for item in analysis:
        report.append("- " + item)

    report.append("")
    report.append("=" * 50)
    report.append("TÓM TẮT")
    report.append("=" * 50)
    report.append(summary)

    report.append("")
    report.append("=" * 50)
    report.append("GỢI Ý LĨNH VỰC PHÙ HỢP")
    report.append("=" * 50)

    if scores.get("logic", 0) > 60 and scores.get("creativity", 0) > 60:
        report.append("- Công nghệ thông tin, AI, kỹ thuật, nghiên cứu.")
    elif scores.get("social", 0) > 60 and scores.get("leadership", 0) > 60:
        report.append("- Kinh doanh, quản lý, marketing, nhân sự.")
    elif scores.get("emotion", 0) > 60:
        report.append("- Giáo dục, tâm lý học, công tác xã hội.")
    else:
        report.append("- Các lĩnh vực yêu cầu tính ổn định và chuyên môn sâu.")

    report.append("")
    report.append("=" * 50)
    report.append("NGHỀ NGHIỆP PHÙ HỢP")
    report.append("=" * 50)
    for career in careers:
        report.append("- " + career)

    return "\n".join(report)