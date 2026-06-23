from __future__ import annotations


class ProbabilityStabilizer:
    def stabilize(
        self,
        base_probability: float,
        confidence_score: float,
        global_mean_probability: float,
        neutral_probability: float | None = None,
    ) -> tuple[float, list[str]]:
        notes: list[str] = []
        confidence = max(0.0, min(1.0, confidence_score))
        smoothed = confidence * base_probability + (1 - confidence) * global_mean_probability

        if confidence < 0.75:
            notes.append("Using smoothed probability estimate")

        if neutral_probability is not None:
            max_delta = 0.18 if confidence >= 0.6 else 0.12
            delta = smoothed - neutral_probability
            if abs(delta) > max_delta:
                smoothed = neutral_probability + max_delta * (1 if delta > 0 else -1)
                notes.append("Limited probability jump from sparse or dominant input features")

        return max(0.01, min(0.98, smoothed)), notes
