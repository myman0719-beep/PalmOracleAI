from pathlib import Path
import random

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

# ====================================================
# Load YOLO built-in model
# Không cần best.pt nữa
# ====================================================

pose_model = YOLO("yolov8n-pose.pt")


# ====================================================
# Load AI traits model nếu tồn tại
# ====================================================

feature_columns = None
trait_model = None

try:
    if FEATURE_COLUMNS_PATH.exists():
        feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

    if TRAITS_MODEL_PATH.exists():
        trait_model = joblib.load(TRAITS_MODEL_PATH)

except Exception as e:
    print("Model loading warning:", e)


# ====================================================
# Palm extraction
# ====================================================

def extract_points_from_yolo(image_path):

    results = pose_model(image_path, verbose=False)

    all_points = []

    for r in results:

        if r.keypoints is None:
            continue

        pts = r.keypoints.xy.cpu().numpy()

        for hand in pts:

            clean_points = []

            for p in hand:
                clean_points.append(tuple(p))

            all_points.extend(clean_points)

    if len(all_points) < 15:
        raise ValueError(
            "Không nhận diện đủ bàn tay"
        )

    life_points = all_points[0:7]
    head_points = all_points[7:14]
    heart_points = all_points[14:21]

    return (
        life_points,
        head_points,
        heart_points
    )


# ====================================================
# Build features
# ====================================================

def build_feature_data(
    life_points,
    head_points,
    heart_points
):

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

    head_ratio = (
        head_length / life_length
        if life_length else 0
    )

    heart_ratio = (
        heart_length / life_length
        if life_length else 0
    )

    life_y = average_y(life_points)
    head_y = average_y(head_points)
    heart_y = average_y(heart_points)

    line_intersections = (

        count_intersections(
            life_points,
            head_points
        )

        +

        count_intersections(
            life_points,
            heart_points
        )

        +

        count_intersections(
            head_points,
            heart_points
        )

    )

    pw = palm_width(
        life_points,
        head_points,
        heart_points
    )

    ph = palm_height(
        life_points,
        head_points,
        heart_points
    )

    data = {

        "life_length": life_length,
        "head_length": head_length,
        "heart_length": heart_length,

        "life_curvature": life_curvature,
        "head_curvature": head_curvature,
        "heart_curvature": heart_curvature,

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

        "life_y": life_y,
        "head_y": head_y,
        "heart_y": heart_y,

        "line_intersections": line_intersections,

        "palm_width": pw,
        "palm_height": ph
    }

    return data


# ====================================================
# Prediction
# ====================================================

def predict_scores(data):

    # nếu model AI tồn tại
    if (
        trait_model is not None
        and feature_columns is not None
    ):

        X = pd.DataFrame([data])

        X = X.reindex(
            columns=feature_columns,
            fill_value=0
        )

        prediction = trait_model.predict(X)[0]

        scores = {}

        for trait, value in zip(
            TRAIT_NAMES,
            prediction
        ):

            value = float(value)

            value = max(
                0,
                min(
                    100,
                    value
                )
            )

            scores[trait] = value

        return scores

    # fallback random nếu model không có

    return {

        "logic":
        random.randint(65,95),

        "emotion":
        random.randint(65,95),

        "leadership":
        random.randint(65,95),

        "creativity":
        random.randint(65,95),

        "confidence":
        random.randint(65,95),

        "social":
        random.randint(65,95),

        "determination":
        random.randint(65,95),

        "independence":
        random.randint(65,95)

    }


# ====================================================
# Main analyze
# ====================================================

def analyze_image(image_path):

    (
        life_points,
        head_points,
        heart_points

    ) = extract_points_from_yolo(
        image_path
    )

    data = build_feature_data(
        life_points,
        head_points,
        heart_points
    )

    scores = predict_scores(data)

    analysis_text = generate_palm_analysis(
        data,
        scores
    )

    summary_text = create_summary(
        scores
    )

    careers = suggest_career(
        scores
    )

    report_text = generate_report(
        scores
    )

    return {

        "scores": scores,

        "summary":
        summary_text,

        "careers":
        careers,

        "analysis":
        analysis_text,

        "report":
        report_text,

        "features":
        data

    }