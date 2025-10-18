# utils.py or services.py (in your app)
from collections import deque
from .models import UserLevelReward, LevelReward
from django.db import transaction

def get_level(members: int, root_user) -> int:
    """
    Given members count, return the corresponding level.
    Uses the 'Total Members Required' sequence.
    """
    level = 1
    total_required = 2  # level 1 total
 
    referrals = root_user.referrals.filter(registration_fee_paid=True).order_by("date_joined")
    total_direct_referrals = referrals.count()
    if total_direct_referrals < 2:
        return 0
    
    while total_required <= members:
        level += 1
        total_required = (2 ** (level + 1)) - 2  # formula for total members required

    return level - 1

def get_paid_downline(root_user):
    """
    Return a set of distinct CustomUser objects that are in root_user's downline
    (exclude root_user) and have registration_fee_paid=True.
    Traversal stops if a user has not paid (like getCommunity).
    """
    visited = set()
    paid_users = set()
    q = deque([root_user])

    while q:
        u = q.popleft()
        if u.id in visited:
            continue
        visited.add(u.id)

        # ✅ Only traverse referrals if current user has paid
        if getattr(u, 'registration_fee_paid', False):
            for ref in u.referrals.all():
                if ref.id not in visited:
                    q.append(ref)

            # add to paid_users (but skip root later)
            paid_users.add(u)

    # ensure root_user not included
    if root_user in paid_users:
        paid_users.remove(root_user)

    return paid_users



@transaction.atomic
def check_and_award_levels(root_user):
    paid_downline = get_paid_downline(root_user)
    paid_count = len(paid_downline)

    available_levels = LevelReward.objects.order_by('level').all()

    achieved_levels = []
    for lr in available_levels:
        required = (2 ** (lr.level + 1)) - 2  # NEW formula
        referrals = root_user.referrals.filter(registration_fee_paid=True).order_by("date_joined")
        total_direct_referrals = referrals.count()

        if paid_count >= required and total_direct_referrals >= 2:
            achieved_levels.append(lr)
        else:
            break

    awarded_levels = set(root_user.user_level_rewards.values_list('level', flat=True))

    for lvl_reward in achieved_levels:
        lvl = lvl_reward.level
        if lvl in awarded_levels:
            continue  # already given

        w = root_user.wallet
        if lvl_reward.withdraw_allowed:
            w.deposit(lvl_reward.reward, locked=False)
        else:
            w.deposit(lvl_reward.reward, locked=True)

        UserLevelReward.objects.create(user=root_user, level=lvl, reward=lvl_reward.reward)

    return {
        'paid_count': paid_count,
        'awarded_levels_now': [lr.level for lr in achieved_levels if lr.level not in awarded_levels],
        'already_awarded_levels': list(awarded_levels),
    }
