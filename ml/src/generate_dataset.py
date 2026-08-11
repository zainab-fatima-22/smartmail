"""
generate_dataset.py
--------------------
Generates ml/data/raw/emails.csv — a SYNTHETIC dataset used to train
the SmartMail classifier.

WHY SYNTHETIC DATA?
A single public dataset that cleanly covers all six categories we need
(Spam, Promotional, Work, Personal, Important, Social) is hard to find —
most public email datasets only cover "spam vs ham". To demonstrate a
real 6-class pipeline, we build our own labeled dataset from templates
and realistic vocabulary variation.

THIS IS NOT REAL-WORLD DATA. It is clearly synthetic, generated from
templates, and documented as such (see ml/data/raw/DATASET_INFO.md).
No private or personal emails were used.

Run:
    python ml/src/generate_dataset.py
"""

import csv
import random
from pathlib import Path

random.seed(42)  # reproducible dataset

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "emails.csv"

# ---------------------------------------------------------------------------
# Template pieces per category. We mix-and-match subjects/senders/bodies to
# generate many realistic-but-synthetic variations instead of hand-typing
# hundreds of individual emails.
# ---------------------------------------------------------------------------

names = ["Alex", "Sam", "Jordan", "Taylor", "Priya", "Ahmed", "Maria", "Chen",
         "Fatima", "John", "Lena", "Omar", "Grace", "Noah", "Sara"]

companies = ["Acme Corp", "Globex", "Initech", "Umbrella Inc", "Wayne Enterprises",
             "Stark Industries", "Hooli", "Nakatomi Trading", "Wonka Industries"]

# ---- SPAM ----
spam_templates = [
    "Congratulations! You have won a ${amount} gift card. Click this link to claim your reward now!",
    "URGENT: You have been selected to receive ${amount} cash prize. Claim before it expires!",
    "You are our lucky winner! Claim your free {item} today, limited time only!",
    "ALERT: Your account has won a special bonus of ${amount}. Verify your details to claim now.",
    "Act now! You qualify for a free {item}. No purchase necessary, click here immediately.",
    "You've been chosen for an exclusive ${amount} reward. Click the link below before midnight!",
    "FINAL NOTICE: Claim your unclaimed prize of ${amount} now or lose it forever!",
    "Free {item} waiting for you! Just click and confirm your shipping address to claim.",
    "You won! Enter your bank details to receive your ${amount} winnings instantly.",
    "Hot singles in your area want to chat with you now, click to view profiles!",
]
spam_amounts = ["500", "1000", "10,000", "250", "5,000", "750"]
spam_items = ["iPhone", "laptop", "vacation package", "gift card", "smartwatch"]

# ---- PROMOTIONAL ----
promo_templates = [
    "Get {pct}% off our {season} collection today only! Shop now before it's gone.",
    "Flash sale: {pct}% off everything at {company} store, this weekend only.",
    "New arrivals just landed! Check out our latest {season} collection now.",
    "Your favorite items are back in stock at {company}. Free shipping on orders over $50.",
    "Exclusive member discount: {pct}% off your next purchase at {company}.",
    "Don't miss our {season} clearance sale — up to {pct}% off select items.",
    "Thanks for shopping with {company}! Here's a {pct}% coupon for your next order.",
    "Last chance: our {season} sale ends tonight. Save {pct}% before midnight.",
    "{company} Rewards: you've earned points! Redeem them for {pct}% off today.",
    "New newsletter from {company}: top picks and deals just for you this week.",
]
promo_pcts = ["10", "20", "30", "40", "50", "70"]
promo_seasons = ["summer", "winter", "spring", "fall", "holiday", "back-to-school"]

# ---- WORK ----
work_templates = [
    "The meeting has been moved to {time} tomorrow. Please update your calendar.",
    "Please review the {doc} before our meeting on {day}.",
    "Reminder: the {project} deadline is {day}. Let me know if you need an extension.",
    "Can you send me the latest version of the {doc} by end of day?",
    "Team standup is at {time} today. Please share your updates in the channel.",
    "I've attached the {doc} for your review. Let's discuss it in tomorrow's sync.",
    "The client requested changes to the {project} proposal. Can we talk today?",
    "Please find attached the {doc} for the {project} project, feedback welcome.",
    "Following up on the {project} status — are we still on track for {day}?",
    "Let's schedule a call to align on the {project} roadmap this {day}.",
]
work_times = ["9 AM", "10 AM", "2 PM", "3 PM", "4:30 PM", "11:15 AM"]
work_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "next week"]
work_docs = ["quarterly report", "project plan", "budget spreadsheet", "presentation deck", "meeting notes"]
work_projects = ["website redesign", "Q3 launch", "migration", "mobile app", "onboarding flow"]

# ---- PERSONAL ----
personal_templates = [
    "Hey, are we still on for dinner this weekend?",
    "Hi {name}, it was great catching up yesterday, let's do it again soon!",
    "Can you believe the game last night? Let's watch the next one together.",
    "Happy birthday! Hope you have an amazing day, let's celebrate this weekend.",
    "Hey, I found that recipe you were asking about, sending it over now.",
    "Are you free to grab coffee this week? It's been too long since we caught up.",
    "Thanks for helping me move last weekend, I really appreciate it!",
    "Hope you're feeling better! Let me know if you need anything.",
    "Just booked the trip for next month, so excited to see you!",
    "Can't wait for the weekend hike, what time should we meet up?",
]

# ---- IMPORTANT ----
important_templates = [
    "Your account requires immediate verification due to a security issue.",
    "Action required: your password will expire in 24 hours, please reset it now.",
    "We detected unusual sign-in activity on your account, please confirm it was you.",
    "Your payment for {company} could not be processed, please update your billing info.",
    "Reminder: your annual review with HR is scheduled for {day} at {time}.",
    "Important: changes to your health insurance plan take effect on {day}.",
    "Your flight on {day} has been rescheduled, please review the new itinerary.",
    "Final reminder: your tax documents are due by {day}, please submit them soon.",
    "Your subscription renewal for {company} failed, please update your payment method.",
    "Notice: scheduled maintenance will affect your account access on {day}.",
]

# ---- SOCIAL ----
social_templates = [
    "Join us for the community event this Saturday at the park!",
    "You have a new friend request on {company} Social.",
    "{name} commented on your recent post, come see what they said!",
    "You've been invited to {name}'s event, tap to RSVP.",
    "Your group '{project} Fans' has 3 new posts today.",
    "Reminder: the neighborhood cleanup event is this {day} morning.",
    "{name} tagged you in a photo, check it out now.",
    "Weekly digest: see what your friends have been up to this week.",
    "You have 5 new notifications waiting for you, tap to view.",
    "Join the local book club meeting this {day} evening at the library.",
]

CATEGORY_TEMPLATES = {
    "spam": spam_templates,
    "promotional": promo_templates,
    "work": work_templates,
    "personal": personal_templates,
    "important": important_templates,
    "social": social_templates,
}

# Small greeting/closing add-ons let us multiply the number of unique
# sentences we can build from a limited set of hand-written templates,
# without the text becoming nonsensical.
OPENERS = ["", "Hi {name}, ", "Hey {name}, ", "Hello, ", "Quick note: ", "FYI - "]
CLOSERS = ["", " Thanks!", " Let me know.", " Talk soon.", " Cheers.", " Best regards."]


def fill(template: str) -> str:
    return template.format(
        amount=random.choice(spam_amounts),
        item=random.choice(spam_items),
        pct=random.choice(promo_pcts),
        season=random.choice(promo_seasons),
        company=random.choice(companies),
        time=random.choice(work_times),
        day=random.choice(work_days),
        doc=random.choice(work_docs),
        project=random.choice(work_projects),
        name=random.choice(names),
    )


def generate_rows(per_category: int = 120):
    rows = []
    for category, templates in CATEGORY_TEMPLATES.items():
        seen = set()
        attempts = 0
        while len(seen) < per_category and attempts < per_category * 40:
            attempts += 1
            template = random.choice(templates)
            opener = fill(random.choice(OPENERS))
            closer = random.choice(CLOSERS)
            body = fill(template)
            # Avoid double-capitalizing when an opener is prepended
            if opener:
                body = body[0].lower() + body[1:]
            text = f"{opener}{body}{closer}".strip()
            if text not in seen:
                seen.add(text)
                rows.append((text, category))
    random.shuffle(rows)
    return rows


def main():
    rows = generate_rows(per_category=120)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["email_text", "category"])
        writer.writerows(rows)
    print(f"Generated {len(rows)} rows -> {OUT_PATH}")
    from collections import Counter
    counts = Counter(c for _, c in rows)
    for cat, n in counts.items():
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
