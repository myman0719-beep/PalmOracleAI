def suggest_career(scores):
    careers = []

    logic = scores.get("logic", 0)
    emotion = scores.get("emotion", 0)
    leadership = scores.get("leadership", 0)
    creativity = scores.get("creativity", 0)
    social = scores.get("social", 0)
    independence = scores.get("independence", 0)
    determination = scores.get("determination", 0)
    confidence = scores.get("confidence", 0)

    if logic >= 60:
        careers.extend(["Software Developer", "Data Analyst", "AI Engineer", "System Engineer"])

    if creativity >= 60:
        careers.extend(["Graphic Designer", "UI/UX Designer", "Content Creator", "Marketing Creative"])

    if social >= 60:
        careers.extend(["Sales Executive", "Customer Success", "HR Specialist", "Public Relations"])

    if leadership >= 60:
        careers.extend(["Project Manager", "Team Leader", "Business Manager"])

    if emotion >= 60:
        careers.extend(["Teacher", "Psychology Assistant", "Counselor", "Social Worker"])

    if independence >= 60:
        careers.extend(["Freelancer", "Consultant", "Researcher"])

    if determination >= 60 and confidence >= 60:
        careers.extend(["Startup Founder", "Product Manager"])

    if len(careers) == 0:
        careers = ["Office Staff", "Administrative Assistant", "Technician", "Accountant", "Customer Support"]

    careers = list(dict.fromkeys(careers))
    return careers[:5]