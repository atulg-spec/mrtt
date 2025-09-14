# utils.py or services.py (in your app)
from collections import deque
from .models import UserLevelReward, LevelReward
from django.db import transaction

def get_paid_downline(root_user):
    """
    Return a set of distinct CustomUser objects that are in root_user's downline
    (exclude root_user) and have registration_fee_paid=True.
    """
    visited = set()
    paid_users = set()
    q = deque([root_user])

    while q:
        u = q.popleft()
        # ensure we don't revisit
        if u.id in visited:
            continue
        visited.add(u.id)

        # iterate referrals of u
        for ref in u.referrals.all():
            if ref.id in visited:
                # already seen
                continue
            q.append(ref)
            # if this referred user paid, add to paid_users (still allow its children to be traversed)
            if getattr(ref, 'registration_fee_paid', False):
                paid_users.add(ref)  # add the model instance (unique by id)

    # ensure root_user not included
    if root_user in paid_users:
        paid_users.remove(root_user)

    return paid_users


@transaction.atomic
def check_and_award_levels(root_user):
    """
    Compute paid downline count and award all newly achieved levels.
    This is idempotent: will not issue a same level reward twice because we record it.
    """
    paid_downline = get_paid_downline(root_user)
    paid_count = len(paid_downline)

    # determine levels available in LevelReward table sorted ascending
    available_levels = LevelReward.objects.order_by('level').all()

    # find which levels are achieved based on absolute counts: 2**level <= paid_count
    # (Note: if your level numbering convention is different you may adapt the formula.)
    # If level numbers in DB are like 1,2,3 representing 2,4,8 then required = 2 ** level
    achieved_levels = []
    for lr in available_levels:
        required = 2 ** lr.level
        if paid_count >= required:
            achieved_levels.append(lr)
        else:
            break

    # get already awarded levels for this user
    awarded_levels = set(root_user.user_level_rewards.values_list('level', flat=True))

    # award newly achieved levels
    for lvl_reward in achieved_levels:
        lvl = lvl_reward.level
        if lvl in awarded_levels:
            continue  # already given

        # Give reward according to withdraw_allowed flag
        w = root_user.wallet  # ensure wallet exists (create wallets for existing users beforehand)
        if lvl_reward.withdraw_allowed:
            w.deposit(lvl_reward.reward, locked=False)
            # apply special T&C: if this is level 4 (as per your rule), set min withdrawal limit
            if lvl == 4:
                w.min_withdraw_limit = max(w.min_withdraw_limit, 200)
                w.save()
        else:
            w.deposit(lvl_reward.reward, locked=True)

        # record that we've given this level
        UserLevelReward.objects.create(user=root_user, level=lvl, reward=lvl_reward.reward)

    # return some useful info (optional)
    return {
        'paid_count': paid_count,
        'awarded_levels_now': [lr.level for lr in achieved_levels if lr.level not in awarded_levels],
        'already_awarded_levels': list(awarded_levels),
    }
