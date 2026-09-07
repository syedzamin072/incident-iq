from classify_node import classify
from eval_set import EVAL_CASES


def run_evaluation():
    correct = 0
    total = len(EVAL_CASES)

    for case in EVAL_CASES:
        result = classify({"alert_text": case["alert_text"]})
        predicted = result["category"]
        expected = case["expected_category"]
        is_correct = predicted == expected

        if is_correct:
            correct += 1

        status = "✓" if is_correct else "✗"
        print(f"{status} '{case['alert_text']}' → predicted: {predicted}, expected: {expected}")

    accuracy = correct / total * 100
    print(f"\nAccuracy: {correct}/{total} ({accuracy:.1f}%)")


if __name__ == "__main__":
    run_evaluation()