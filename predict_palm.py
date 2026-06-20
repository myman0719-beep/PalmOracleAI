from pathlib import Path

from ultralytics import YOLO
from report_generator import generate_report
from palm_logic import generate_palm_analysis
from summary_engine import create_summary
from career_engine import suggest_career
from utils import (
    average_y,
    bbox_size,
    count_intersections,
    curvature,
    curve_length,
    line_angle,
    max_curvature,
    palm_height,
    palm_width
)

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
YOLO_MODEL = BASE_DIR / "runs" / "pose" / "train-5" / "weights" / "best.pt"
FEATURE_COLUMNS_PATH = BASE_DIR / "feature_columns.pkl"
TRAITS_MODEL_PATH = BASE_DIR / "traits_model.pkl"

TRAIT_NAMES = [
    "logic",
    "emotion",
    "leadership",
    "creativity",
    "confidence",
    "social",
    "determination",
    "independence"
]

pose_model = YOLO(str(YOLO_MODEL))
feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
trait_model = joblib.load(TRAITS_MODEL_PATH)


def extract_points_from_yolo(image_path):
    results = pose_model(image_path, verbose=False)

    life_points = None
    head_points = None
    heart_points = None

    for r in results:
        classes = r.boxes.cls.cpu().numpy()
        keypoints = r.keypoints.xy.cpu().numpy()

        for cls_id, pts in zip(classes, keypoints):
            pts = [tuple(p) for p in pts]

            if int(cls_id) == 3:
                life_points = pts
            elif int(cls_id) == 1:
                head_points = pts
            elif int(cls_id) == 2:
                heart_points = pts

    if life_points is None or head_points is None or heart_points is None:
        raise ValueError("Không tìm thấy đủ 3 đường chỉ tay.")

    return life_points, head_points, heart_points


def build_feature_data(life_points, head_points, heart_points):
    life_length = curve_length(life_points)
    head_length = curve_length(head_points)
    heart_length = curve_length(heart_points)

    life_curvature = curvature(life_points)
    head_curvature = curvature(head_points)
    heart_curvature = curvature(heart_points)

    life_max_curvature = max_curvature(life_points)
    head_max_curvature = max_curvature(head_points)
    heart_max_curvature = max_curvature(heart_points)

    life_angle = line_angle(life_points)
    head_angle = line_angle(head_points)
    heart_angle = line_angle(heart_points)

    life_bbox_width, life_bbox_height = bbox_size(life_points)
    head_bbox_width, head_bbox_height = bbox_size(head_points)
    heart_bbox_width, heart_bbox_height = bbox_size(heart_points)

    head_ratio = life_length and head_length / life_length or 0
    heart_ratio = life_length and heart_length / life_length or 0
    head_heart_ratio = heart_length and head_length / heart_length or 0

    life_y = average_y(life_points)
    head_y = average_y(head_points)
    heart_y = average_y(heart_points)

    head_heart_gap = abs(head_y - heart_y)
    life_head_gap = abs(life_y - head_y)
    life_heart_gap = abs(life_y - heart_y)

    line_intersections = (
        count_intersections(life_points, head_points)
        + count_intersections(life_points, heart_points)
        + count_intersections(head_points, heart_points)
    )

    pw = palm_width(life_points, head_points, heart_points)
    ph = palm_height(life_points, head_points, heart_points)

    total_length = life_length + head_length + heart_length if (life_length + head_length + heart_length) else 1.0

    life_length_ratio = life_length / total_length
    head_length_ratio = head_length / total_length
    heart_length_ratio = heart_length / total_length

    life_aspect = life_bbox_width / (life_bbox_height + 1e-6)
    head_aspect = head_bbox_width / (head_bbox_height + 1e-6)
    heart_aspect = heart_bbox_width / (heart_bbox_height + 1e-6)

    life_pos = life_y / ph if ph else 0
    head_pos = head_y / ph if ph else 0
    heart_pos = heart_y / ph if ph else 0

    data = {
        "life_length": life_length,
        "head_length": head_length,
        "heart_length": heart_length,
        "life_curvature": life_curvature,
        "head_curvature": head_curvature,
        "heart_curvature": heart_curvature,
        "life_max_curvature": life_max_curvature,
        "head_max_curvature": head_max_curvature,
        "heart_max_curvature": heart_max_curvature,
        "life_angle": life_angle,
        "head_angle": head_angle,
        "heart_angle": heart_angle,
        "life_bbox_width": life_bbox_width,
        "life_bbox_height": life_bbox_height,
        "head_bbox_width": head_bbox_width,
        "head_bbox_height": head_bbox_height,
        "heart_bbox_width": heart_bbox_width,
        "heart_bbox_height": heart_bbox_height,
        "head_ratio": head_ratio,
        "heart_ratio": heart_ratio,
        "head_heart_ratio": head_heart_ratio,
        "life_y": life_y,
        "head_y": head_y,
        "heart_y": heart_y,
        "head_heart_gap": head_heart_gap,
        "life_head_gap": life_head_gap,
        "life_heart_gap": life_heart_gap,
        "line_intersections": line_intersections,
        "palm_width": pw,
        "palm_height": ph,
        "life_length_ratio": life_length_ratio,
        "head_length_ratio": head_length_ratio,
        "heart_length_ratio": heart_length_ratio,
        "life_aspect": life_aspect,
        "head_aspect": head_aspect,
        "heart_aspect": heart_aspect,
        "life_pos": life_pos,
        "head_pos": head_pos,
        "heart_pos": heart_pos
    }

    return data


def predict_scores(data):
    X = pd.DataFrame([data])
    X = X.reindex(columns=feature_columns, fill_value=0)

    prediction = trait_model.predict(X)[0]

    scores = {}
    for trait, value in zip(TRAIT_NAMES, prediction):
        value = float(value)
        value = max(0, min(100, value))
        scores[trait] = value

    return scores


def analyze_image(image_path):
    life_points, head_points, heart_points = extract_points_from_yolo(image_path)
    data = build_feature_data(life_points, head_points, heart_points)
    scores = predict_scores(data)

    analysis_text = generate_palm_analysis(data, scores)
    summary_text = create_summary(scores)
    careers = suggest_career(scores)
    report_text = generate_report(scores)

    return {
        "scores": scores,
        "summary": summary_text,
        "careers": careers,
        "analysis": analysis_text,
        "report": report_text,
        "features": data
    }