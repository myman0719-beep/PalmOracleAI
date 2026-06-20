def create_summary(scores):
    top_trait = max(scores, key=scores.get)
    top_score = scores[top_trait]

    if top_score >= 70:
        mapping = {
            "logic": "Bạn nổi bật với khả năng tư duy logic và phân tích vấn đề.",
            "emotion": "Bạn là người giàu cảm xúc và có khả năng đồng cảm tốt.",
            "leadership": "Bạn có tố chất lãnh đạo và khả năng dẫn dắt người khác.",
            "creativity": "Bạn sở hữu khả năng sáng tạo nổi bật và nhiều ý tưởng mới.",
            "confidence": "Bạn có sự tự tin cao trong công việc và cuộc sống.",
            "social": "Bạn dễ dàng xây dựng các mối quan hệ và hòa nhập với tập thể.",
            "determination": "Bạn là người rất kiên trì và theo đuổi mục tiêu đến cùng.",
            "independence": "Bạn có tính độc lập cao và thích tự đưa ra quyết định."
        }
        return mapping[top_trait]

    if top_score >= 50:
        mapping = {
            "logic": "Bạn có khả năng phân tích và suy nghĩ khá tốt.",
            "emotion": "Bạn có sự cân bằng tương đối giữa cảm xúc và lý trí.",
            "leadership": "Bạn có thể đảm nhận vai trò dẫn dắt khi cần thiết.",
            "creativity": "Bạn có tư duy linh hoạt và khả năng nhìn nhận nhiều góc độ.",
            "confidence": "Bạn có mức độ tự tin khá tốt.",
            "social": "Bạn giao tiếp khá tốt và duy trì các mối quan hệ tích cực.",
            "determination": "Bạn có tinh thần cố gắng và trách nhiệm cao.",
            "independence": "Bạn có khả năng tự giải quyết nhiều vấn đề của bản thân."
        }
        return mapping[top_trait]

    return "Các chỉ số hiện tại chưa cho thấy một đặc điểm nổi trội rõ ràng. Bạn có xu hướng cân bằng giữa nhiều khía cạnh tính cách khác nhau."