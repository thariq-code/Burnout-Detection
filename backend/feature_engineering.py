from datetime import datetime
from collections import defaultdict
import numpy as np
from sentiment import get_sentiment

def compute_features(commits):
    """
    commits: list of dicts with keys 'date' (ISO string) and 'message'
    Returns a dict of engineered features.
    """
    # Parse commit datetimes
    for c in commits:
        c["dt"] = datetime.fromisoformat(c["date"].replace("Z", "+00:00"))

    # Sort by date
    commits.sort(key=lambda x: x["dt"])

    # 1. Commit frequency (average commits per week over the period)
    weeks = defaultdict(int)
    for c in commits:
        week = c["dt"].strftime("%Y-%W")
        weeks[week] += 1
    weekly_freq = np.mean(list(weeks.values())) if weeks else 0

    # 2. Night coding ratio (commits between 10PM and 5AM)
    night_commits = 0
    for c in commits:
        hour = c["dt"].hour
        if hour >= 22 or hour < 5:
            night_commits += 1
    night_ratio = night_commits / len(commits) if commits else 0

    # 3. Weekend coding ratio
    weekend_commits = 0
    for c in commits:
        if c["dt"].weekday() >= 5:
            weekend_commits += 1
    weekend_ratio = weekend_commits / len(commits) if commits else 0

    # 4. Bug-fix keyword frequency
    bug_keywords = ["fix", "bug", "issue", "error", "crash", "patch", "resolve"]
    bug_count = 0
    for c in commits:
        msg = c["message"].lower()
        if any(kw in msg for kw in bug_keywords):
            bug_count += 1
    bug_freq = bug_count / len(commits) if commits else 0

    # 5. Average sentiment
    sentiments = [get_sentiment(c["message"]) for c in commits]
    avg_sentiment = np.mean(sentiments) if sentiments else 0

    # 6. Activity consistency score (inverse of variance in daily commits)
    days = defaultdict(int)
    for c in commits:
        day = c["dt"].date().isoformat()
        days[day] += 1
    if len(days) > 1:
        daily_commits = list(days.values())
        consistency = 1 / (np.std(daily_commits) + 1e-5)  # higher = more consistent
    else:
        consistency = 1.0

    # 7. Stress pattern indicator (e.g., high night + weekend + low sentiment)
    stress_indicator = (night_ratio * 0.4 + weekend_ratio * 0.3 + (1 - avg_sentiment) * 0.3)

    return {
        "weekly_commit_frequency": weekly_freq,
        "night_coding_ratio": night_ratio,
        "weekend_coding_ratio": weekend_ratio,
        "bug_fix_keyword_frequency": bug_freq,
        "average_sentiment": avg_sentiment,
        "activity_consistency": consistency,
        "stress_pattern_indicator": stress_indicator,
        "commit_count": len(commits)
    }