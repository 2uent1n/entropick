import random
from dataclasses import dataclass
from typing import Any


@dataclass
class Reviewer:
    slack_id: str
    name: str
    is_available: bool = True
    weight: float = 1.0
    times_selected: int = 0
    times_available: int = 0

    def __hash__(self) -> int:
        # Required to use Reviewer in a set
        return hash(self.slack_id)

    def __eq__(self, other: Any) -> bool:
        # Two reviewers are equal if they have the same slack_id
        if not isinstance(other, Reviewer):
            return False
        return self.slack_id == other.slack_id


class ReviewerPool:
    def __init__(self, name: str):
        self.name: str = name
        self.reviewers: set[Reviewer] = set()
        self.total_selections: int = 0

    def add_reviewer(self, reviewer: Reviewer) -> None:
        """Adds a reviewer to the pool."""
        self.reviewers.add(reviewer)

    def remove_reviewer(self, reviewer: Reviewer) -> None:
        """Removes a reviewer from the pool."""
        self.reviewers.discard(reviewer)

    def get_available_reviewers(self) -> list[Reviewer]:
        """Returns the list of available reviewers."""
        return [reviewer for reviewer in self.reviewers if reviewer.is_available]

    def _calculate_fair_weights(self, reviewers: list[Reviewer]) -> list[float]:
        """
        Calculates fair weights based on selection deficit/surplus.

        The more a reviewer is "behind" their fair share, the higher their weight.

        Args:
            reviewers: List of available reviewers

        Returns:
            List of weights that promote fairness
        """
        if not reviewers:
            return []

        # Calculate each reviewer's "fair share" of selections
        total_availability = sum(r.times_available for r in reviewers)

        if total_availability == 0:
            # No history yet, use equal weights
            return [1.0] * len(reviewers)

        weights = []
        for reviewer in reviewers:
            # Calculate expected selections based on availability ratio
            if total_availability > 0:
                expected_selections = (
                    reviewer.times_available / total_availability
                ) * self.total_selections
            else:
                expected_selections = 0

            # Calculate deficit (positive = should be selected more, negative = selected too much)
            deficit = expected_selections - reviewer.times_selected

            # Convert deficit to weight (minimum weight of 0.1 to ensure everyone has a chance)
            # Higher deficit = higher weight
            weight = max(0.1, 1.0 + deficit)
            weights.append(weight)

        return weights

    def get_reviewers_weights(
        self, reviewers: list[Reviewer] | None = None
    ) -> list[float]:
        """
        Extracts fair weights for reviewers based on selection history.

        Args:
            reviewers: Optional list of reviewers. If None, uses all available reviewers.

        Returns:
            List of fair weights corresponding to reviewers in the same order.
        """
        if reviewers is None:
            reviewers = self.get_available_reviewers()

        return self._calculate_fair_weights(reviewers)

    def get_reviewers_and_weights(
        self, reviewers: list[Reviewer] | None = None
    ) -> tuple[list[Reviewer], list[float]]:
        """
        Returns both the list of reviewers and their corresponding fair weights.

        Args:
            reviewers: Optional list of reviewers. If None, uses all available reviewers.

        Returns:
            Tuple containing (reviewer_list, weights_list)
        """
        if reviewers is None:
            reviewers = self.get_available_reviewers()

        weights = self.get_reviewers_weights(reviewers)
        return reviewers, weights

    def update_stats_after_selection(self, selected_reviewers: list[Reviewer]) -> None:
        """
        Updates selection statistics after a selection has been made.

        Args:
            selected_reviewers: List of reviewers that were selected
        """
        selected_ids = {reviewer.slack_id for reviewer in selected_reviewers}

        # Update availability count for all available reviewers
        for reviewer in self.reviewers:
            if reviewer.is_available:
                reviewer.times_available += 1

                # Update selection count for selected reviewers
                if reviewer.slack_id in selected_ids:
                    reviewer.times_selected += 1

        # Update total selections
        self.total_selections += len(selected_reviewers)

    def pick_n_reviewers(
        self,
        n: int,
        reviewers: list[Reviewer] | None = None,
        auto_update_stats: bool = True,
    ) -> list[Reviewer]:
        """
        Randomly selects N reviewers using fair weights based on selection history.

        Args:
            n: Number of reviewers to select.
            reviewers: Optional list of reviewers. If None, uses all available reviewers.
            auto_update_stats: Whether to automatically update statistics after selection.

        Returns:
            A list of N selected reviewers.

        Raises:
            ValueError: If no reviewers are available for selection.
        """
        reviewers, weights = self.get_reviewers_and_weights(reviewers)

        if len(reviewers) < n:
            raise ValueError(
                f"Not enough reviewers available. Requested: {n}, Available: {len(reviewers)}"
            )

        selected = random.choices(reviewers, weights=weights, k=n)

        if auto_update_stats:
            self.update_stats_after_selection(selected)

        return selected

    def pick_reviewer(
        self, reviewers: list[Reviewer] | None = None, auto_update_stats: bool = True
    ) -> Reviewer:
        """
        Randomly selects a reviewer using fair weights based on selection history.

        Args:
            reviewers: Optional list of reviewers. If None, uses all available reviewers.
            auto_update_stats: Whether to automatically update statistics after selection.
        """
        return self.pick_n_reviewers(1, reviewers, auto_update_stats)[0]

    def get_fairness_summary(self) -> dict[str, dict]:
        """
        Returns a summary of fairness metrics for all reviewers.

        Returns:
            Dictionary with detailed fairness stats for each reviewer.
        """
        total_availability = sum(
            r.times_available for r in self.reviewers if r.times_available > 0
        )

        summary = {}
        for reviewer in self.reviewers:
            if reviewer.times_available > 0:
                expected_selections = (
                    reviewer.times_available / total_availability
                ) * self.total_selections
                deficit = expected_selections - reviewer.times_selected
                selection_rate = reviewer.times_selected / reviewer.times_available
            else:
                expected_selections = 0
                deficit = 0
                selection_rate = 0

            summary[reviewer.name] = {
                "times_selected": reviewer.times_selected,
                "times_available": reviewer.times_available,
                "expected_selections": round(expected_selections, 2),
                "deficit": round(deficit, 2),
                "selection_rate": round(selection_rate, 3),
                "current_weight": round(max(0.1, 1.0 + deficit), 2),
            }

        return summary

    def reset_all_stats(self) -> None:
        """
        Resets all selection statistics and weights.
        """
        for reviewer in self.reviewers:
            reviewer.times_selected = 0
            reviewer.times_available = 0
            reviewer.weight = 1.0
        self.total_selections = 0
