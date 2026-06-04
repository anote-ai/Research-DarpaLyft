"""Tests for continual learning metrics and task sequence generation."""
from __future__ import annotations

import pytest

from darpalyft.core import TaskDomain, TaskRecord, TaskSequence
from darpalyft.data import (
    make_catastrophic_forgetting_sequence,
    make_iid_sequence,
    make_task_record,
    make_task_sequence,
)
from darpalyft.evaluate import (
    backward_transfer,
    continual_learning_score,
    domain_drift_penalty,
    forward_transfer,
    plasticity_score,
    stability_score,
)


# ---------------------------------------------------------------------------
# TaskRecord validation
# ---------------------------------------------------------------------------


def test_task_record_valid() -> None:
    r = TaskRecord(
        task_id="T0",
        domain=TaskDomain.URBAN,
        accuracy_after_training=0.80,
        accuracy_after_later=0.75,
        accuracy_before_training=0.10,
    )
    assert r.accuracy_after_training == 0.80


def test_task_record_invalid_accuracy() -> None:
    with pytest.raises(ValueError):
        TaskRecord(
            task_id="T0",
            domain=TaskDomain.URBAN,
            accuracy_after_training=1.5,  # out of range
        )


# ---------------------------------------------------------------------------
# TaskSequence helpers
# ---------------------------------------------------------------------------


def test_task_sequence_domain_drift() -> None:
    seq = make_task_sequence(n_tasks=6, seed=42, domain_drift=True)
    assert len(seq.records) == 6
    assert seq.domain_drift_count() >= 1


def test_iid_sequence_no_drift() -> None:
    seq = make_iid_sequence(n_tasks=5, seed=1)
    assert seq.domain_drift_count() == 0


def test_catastrophic_forgetting_sequence() -> None:
    seq = make_catastrophic_forgetting_sequence(n_tasks=4, seed=7)
    assert len(seq.records) == 4
    # All should have severe forgetting (accuracy_after_later < accuracy_after_training)
    for r in seq.records:
        assert r.accuracy_after_later < r.accuracy_after_training


# ---------------------------------------------------------------------------
# Backward transfer
# ---------------------------------------------------------------------------


def test_backward_transfer_negative_on_forgetting() -> None:
    seq = make_catastrophic_forgetting_sequence(n_tasks=5, seed=0)
    bwt = backward_transfer(seq)
    assert bwt < 0  # forgetting => negative BWT


def test_backward_transfer_zero_no_valid_records() -> None:
    seq = TaskSequence(records=[
        TaskRecord(task_id="T0", domain=TaskDomain.URBAN, accuracy_after_training=0.8)
    ])
    assert backward_transfer(seq) == 0.0


def test_backward_transfer_positive_plasticity() -> None:
    # Create records where accuracy improves after later tasks
    records = [
        TaskRecord("T0", TaskDomain.URBAN, 0.7, accuracy_after_later=0.85),
        TaskRecord("T1", TaskDomain.MARITIME, 0.75, accuracy_after_later=0.80),
    ]
    seq = TaskSequence(records=records)
    assert backward_transfer(seq) > 0


# ---------------------------------------------------------------------------
# Forward transfer
# ---------------------------------------------------------------------------


def test_forward_transfer_range() -> None:
    seq = make_task_sequence(n_tasks=6, seed=10)
    fwt = forward_transfer(seq)
    assert 0.0 <= fwt <= 1.0


def test_forward_transfer_zero_no_valid_records() -> None:
    seq = TaskSequence(records=[
        TaskRecord(task_id="T0", domain=TaskDomain.DESERT, accuracy_after_training=0.8)
    ])
    assert forward_transfer(seq) == 0.0


# ---------------------------------------------------------------------------
# Composite continual learning score
# ---------------------------------------------------------------------------


def test_continual_learning_score_range() -> None:
    seq = make_task_sequence(n_tasks=6, seed=42)
    score = continual_learning_score(seq)
    assert 0.0 <= score <= 1.0


def test_continual_learning_score_catastrophic() -> None:
    seq = make_catastrophic_forgetting_sequence(n_tasks=5)
    score = continual_learning_score(seq)
    # Severe forgetting should drive score below 0.5
    assert score < 0.5


# ---------------------------------------------------------------------------
# Plasticity and stability
# ---------------------------------------------------------------------------


def test_plasticity_score_range() -> None:
    seq = make_task_sequence(n_tasks=4, seed=0)
    p = plasticity_score(seq)
    assert 0.0 <= p <= 1.0


def test_stability_score_perfect() -> None:
    records = [
        TaskRecord("T0", TaskDomain.URBAN, 0.8, accuracy_after_later=0.85),
        TaskRecord("T1", TaskDomain.MARITIME, 0.75, accuracy_after_later=0.80),
    ]
    seq = TaskSequence(records=records)
    assert stability_score(seq) == 1.0


def test_stability_score_zero_all_forget() -> None:
    seq = make_catastrophic_forgetting_sequence(n_tasks=5)
    s = stability_score(seq)
    assert s == 0.0


# ---------------------------------------------------------------------------
# Domain drift penalty
# ---------------------------------------------------------------------------


def test_domain_drift_penalty_iid() -> None:
    seq = make_iid_sequence(n_tasks=5)
    assert domain_drift_penalty(seq) == 0.0


def test_domain_drift_penalty_max_drift() -> None:
    # Alternating two different domains => maximum drift
    records = [
        TaskRecord(f"T{i}", TaskDomain.URBAN if i % 2 == 0 else TaskDomain.ARCTIC, 0.8)
        for i in range(6)
    ]
    seq = TaskSequence(records=records)
    penalty = domain_drift_penalty(seq)
    assert penalty == 1.0


def test_domain_drift_penalty_single_task() -> None:
    seq = TaskSequence(records=[
        TaskRecord("T0", TaskDomain.URBAN, 0.8)
    ])
    assert domain_drift_penalty(seq) == 0.0
