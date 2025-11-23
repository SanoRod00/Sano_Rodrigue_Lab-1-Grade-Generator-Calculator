#!/usr/bin/env python3
"""Interactive Grade Generator Calculator."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Assignment:
    name: str
    category: str  # "FA" or "SA"
    grade: float   # 0-100
    weight: float  # >0

    @property
    def weighted_score(self) -> float:
        return (self.grade / 100) * self.weight


def prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Value cannot be empty. Please try again.")


def prompt_category() -> str:
    while True:
        category = input('Category ("FA" or "SA"): ').strip().upper()
        if category in {"FA", "SA"}:
            return category
        print('Invalid category. Please enter "FA" or "SA".')


def prompt_float(
    prompt: str,
    min_value: float | None = None,
    max_value: float | None = None,
    strict_greater: bool = False,
) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("Please enter a numeric value.")
            continue

        if min_value is not None:
            if strict_greater and value <= min_value:
                print(f"Value must be greater than {min_value}.")
                continue
            if not strict_greater and value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
        if max_value is not None and value > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return value


def collect_assignments() -> list[Assignment]:
    assignments: list[Assignment] = []
    print("Enter assignments. When finished, type 'n' when asked to add another.")

    while True:
        name = prompt_non_empty("Assignment name: ")
        category = prompt_category()
        grade = prompt_float("Grade (0-100): ", min_value=0, max_value=100)
        weight = prompt_float("Weight (positive number): ", min_value=0, strict_greater=True)

        assignments.append(Assignment(name=name, category=category, grade=grade, weight=weight))

        again = input("Add another assignment? (y/n): ").strip().lower()
        if again not in {"y", "yes", ""}:
            break

    return assignments


def summarize(assignments: list[Assignment]) -> None:
    fa_weight = sum(a.weight for a in assignments if a.category == "FA")
    sa_weight = sum(a.weight for a in assignments if a.category == "SA")
    fa_total = sum(a.weighted_score for a in assignments if a.category == "FA")
    sa_total = sum(a.weighted_score for a in assignments if a.category == "SA")

    final_grade = fa_total + sa_total
    gpa = (final_grade / 100) * 5

    fa_pass = fa_weight == 0 or fa_total >= 0.5 * fa_weight
    sa_pass = sa_weight == 0 or sa_total >= 0.5 * sa_weight
    passed = fa_pass and sa_pass

    print("\n--- Grade Summary ---")
    for idx, a in enumerate(assignments, start=1):
        print(
            f"{idx}. {a.name} [{a.category}] "
            f"Grade: {a.grade:.2f} | Weight: {a.weight:.2f} | Weighted: {a.weighted_score:.2f}"
        )

    print(f"\nFA total: {fa_total:.2f} / {fa_weight:.2f}")
    print(f"SA total: {sa_total:.2f} / {sa_weight:.2f}")
    print(f"Final grade: {final_grade:.2f}")
    print(f"GPA (5-point scale): {gpa:.2f}")
    print(f"Pass status: {'PASS' if passed else 'FAIL'}")
    print(resubmission_message(assignments))


def resubmission_message(assignments: list[Assignment]) -> str:
    """Return a short resubmission note based on failed formative assignments."""
    failing_fa = [a for a in assignments if a.category == "FA" and a.grade < 50]
    if not failing_fa:
        return "Resubmission: no failed formative assignments."

    if len(failing_fa) == 1:
        a = failing_fa[0]
        return f"Resubmission: {a.name} (FA) is eligible to resubmit."

    # Multiple failed FAs: pick the one with the highest weight, or list ties.
    max_weight = max(a.weight for a in failing_fa)
    top_failures = [a for a in failing_fa if a.weight == max_weight]
    if len(top_failures) == 1:
        a = top_failures[0]
        return f"Resubmission: choose {a.name} (highest-weight failed FA)."

    tied_names = ", ".join(a.name for a in top_failures)
    return f"Resubmission: choose one of {tied_names} (tied highest-weight failed FAs)."


def write_csv(assignments: list[Assignment], path: Path) -> None:
    with path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Assignment", "Category", "Grade", "Weight"])
        for a in assignments:
            writer.writerow([a.name, a.category, f"{a.grade:.2f}", f"{a.weight:.2f}"])


def main() -> None:
    assignments = collect_assignments()
    if not assignments:
        print("No assignments were entered. Exiting.")
        return

    summarize(assignments)

    csv_path = Path("grades.csv")
    write_csv(assignments, csv_path)
    print(f"\nSaved CSV to {csv_path.resolve()}")


if __name__ == "__main__":
    main()
