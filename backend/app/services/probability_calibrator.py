from __future__ import annotations

from app.services.probability_stabilizer import ProbabilityStabilizer


class ProbabilityCalibrator:
    def __init__(self) -> None:
        self.stabilizer = ProbabilityStabilizer()

    def calibrate(
        self,
        raw_probability: float,
        confidence_score: float,
        global_mean_probability: float,
        neutral_probability: float | None,
    ) -> tuple[float, list[str]]:
        calibrated, notes = self.stabilizer.stabilize(
            base_probability=raw_probability,
            confidence_score=confidence_score,
            global_mean_probability=global_mean_probability,
            neutral_probability=neutral_probability,
        )
        if abs(calibrated - raw_probability) >= 0.01:
            notes.append("Calibrated raw model probability using confidence and global base rate")
        return calibrated, notes
