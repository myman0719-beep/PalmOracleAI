def get_palm_type(features):
    life = features.get("life_length", 0)
    head = features.get("head_length", 0)
    heart = features.get("heart_length", 0)

    total = life + head + heart
    avg = total / 3 if total else 0

    life_long = int(life > avg)
    head_long = int(head > avg)
    heart_long = int(heart > avg)

    code = f"{life_long}{head_long}{heart_long}"

    mapping = {
        "111": "Sinh-Tri-Tâm dài",
        "110": "Sinh-Tri dài, Tâm ngắn",
        "101": "Sinh-Tâm dài, Trí ngắn",
        "011": "Trí-Tâm dài, Sinh ngắn",
        "100": "Sinh dài, Trí-Tâm ngắn",
        "010": "Trí dài, Sinh-Tâm ngắn",
        "001": "Tâm dài, Sinh-Trí ngắn",
        "000": "Cả 3 đường ngắn"
    }

    return mapping.get(code, "Không xác định")


def generate_palm_analysis(features, scores):
    result = []

    life = features.get("life_length", 0)
    head = features.get("head_length", 0)
    heart = features.get("heart_length", 0)
    life_curv = features.get("life_curvature", 0)

    palm_type = get_palm_type(features)

    result.append(f"Loại chỉ tay: {palm_type}")
    result.append("")

    if head > life * 1.15:
        result.append("Đường trí đạo nổi bật cho thấy bạn có xu hướng suy nghĩ sâu và phân tích kỹ trước khi hành động.")
    elif head < life * 0.85:
        result.append("Bạn thường đưa ra quyết định nhanh và tin vào kinh nghiệm thực tế.")
    else:
        result.append("Bạn có sự cân bằng tương đối giữa lý trí và hành động.")

    if heart > head:
        result.append("Cảm xúc đóng vai trò quan trọng trong các mối quan hệ và quyết định cá nhân.")
    elif heart < head * 0.8:
        result.append("Bạn có xu hướng giữ lý trí cao hơn cảm xúc.")
    else:
        result.append("Bạn có khả năng cân bằng giữa cảm xúc và lý trí.")

    if life > head and life > heart:
        result.append("Đường sinh đạo nổi bật cho thấy tinh thần kiên trì và khả năng theo đuổi mục tiêu lâu dài.")

    if life_curv > 2:
        result.append("Bạn dễ thích nghi với môi trường mới và linh hoạt trong cách xử lý vấn đề.")
    else:
        result.append("Bạn có xu hướng ổn định và thích những kế hoạch rõ ràng.")

    if scores.get("logic", 0) > 60:
        result.append("Khả năng tư duy logic được đánh giá khá cao.")
    if scores.get("creativity", 0) > 60:
        result.append("Bạn có tư duy sáng tạo và thường tìm cách tiếp cận mới.")
    if scores.get("social", 0) > 60:
        result.append("Bạn dễ dàng giao tiếp và xây dựng các mối quan hệ.")
    if scores.get("confidence", 0) > 60:
        result.append("Bạn có mức độ tự tin khá tốt trong công việc và cuộc sống.")

    return "\n".join(result)