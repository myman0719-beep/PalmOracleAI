def analyze_personality(scores):
    result = []

    logic = scores.get("logic", 0)
    emotion = scores.get("emotion", 0)
    leadership = scores.get("leadership", 0)
    creativity = scores.get("creativity", 0)
    confidence = scores.get("confidence", 0)
    social = scores.get("social", 0)
    determination = scores.get("determination", 0)
    independence = scores.get("independence", 0)

    if emotion > logic + 15:
        result.append("Bạn có xu hướng đưa ra quyết định dựa nhiều vào trực giác và cảm nhận cá nhân.")
    elif logic > emotion + 15:
        result.append("Bạn thường phân tích kỹ vấn đề trước khi đưa ra quyết định.")
    else:
        result.append("Bạn có xu hướng cân bằng giữa cảm xúc và tư duy phân tích.")

    if social < 40:
        result.append("Bạn thích môi trường yên tĩnh và thoải mái hơn khi làm việc độc lập hoặc trong nhóm nhỏ.")
    elif social > 60:
        result.append("Bạn dễ hòa nhập với tập thể và thường chủ động trong giao tiếp.")

    if leadership < 40:
        result.append("Bạn thích vai trò hỗ trợ, phối hợp hơn là dẫn dắt tập thể.")
    elif leadership > 60:
        result.append("Bạn có xu hướng chủ động dẫn dắt và tổ chức công việc cho người khác.")

    if creativity > 60:
        result.append("Bạn có khả năng nhìn nhận vấn đề từ nhiều góc độ và thường đưa ra ý tưởng mới.")
    elif creativity >= 40:
        result.append("Bạn có tư duy linh hoạt nhưng vẫn ưu tiên giải pháp thực tế.")

    if confidence < 40:
        result.append("Bạn thường cân nhắc khá kỹ trước khi hành động.")
    elif confidence > 60:
        result.append("Bạn khá tự tin vào năng lực của bản thân và sẵn sàng thử thách mới.")

    if determination > 60:
        result.append("Khi đã xác định mục tiêu, bạn thường kiên trì theo đuổi đến cùng.")
    elif determination < 40:
        result.append("Bạn có xu hướng điều chỉnh kế hoạch linh hoạt khi gặp trở ngại.")

    if independence > 60:
        result.append("Bạn thích tự chủ trong công việc và ra quyết định dựa trên đánh giá cá nhân.")
    elif independence < 40:
        result.append("Bạn thường tham khảo ý kiến người khác trước khi đưa ra quyết định quan trọng.")

    return result