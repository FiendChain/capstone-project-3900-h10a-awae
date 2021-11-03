from server import app, get_db
from flask_login import current_user

# update level after a purchase 
def refresh_cafepass_level(db, info):
    net_xp = info['net_xp']
    curr_level = 1
    for i in range(1, 20):
        level = db.get_entries_by_heading("level", "level", i)
        if not level:
            break
        level = level[0]
        level_xp = level['xp']

        curr_level = i
        if level_xp > net_xp:
            break
    
    return curr_level
    

class CafepassInfo:
    def __init__(self, info, db):
        self.level = info['level']
        self.id = info['id']
        self.user_id = info['user_id']
        self.paid = info['paid']
        self.net_xp = info['net_xp']

        assert self.level > 0

        curr_level = db.get_entries_by_heading("level", "level", self.level)
        prev_level = db.get_entries_by_heading("level", "level", self.level-1)

        curr_level = curr_level[0] if curr_level else None
        prev_level = prev_level[0] if prev_level else None

        assert curr_level
        assert prev_level

        self.curr_level_info = curr_level
        self.prev_level_info = prev_level
    
    @property
    def frac_complete(self):
        remaining_xp = self.remaining_xp
        if remaining_xp == 0:
            return 1

        delta = self.curr_level_info['xp']-self.prev_level_info['xp']
        completed_level_xp = self.net_xp-self.prev_level_info['xp']
        return min(1, completed_level_xp / delta)
    
    @property
    def percent_complete(self):
        return self.frac_complete * 100
    
    @property
    def frac_discount(self):
        if self.paid:
            return self.curr_level_info['discount_paid']
        return self.curr_level_info['discount_free']
    
    @property
    def percent_discount(self):
        return self.frac_discount * 100

    # Calculate total xp till next level
    @property
    def remaining_xp(self):
        return max(0, self.curr_level_info['xp']-self.net_xp)
    
    @property
    def curr_milestone(self):
        return self.curr_level_info['xp']
    
    @property
    def prev_milestone(self):
        return self.prev_level_info and self.prev_level_info['xp']
    
def get_cafepass(user_id=None):
    if user_id is None:
        user_id = current_user.get_id()

    with app.app_context():
        db = get_db()
        cafepass = db.get_entries_by_heading("cafepass", "user_id", user_id)

    if cafepass:
        cafepass = cafepass[0]
    else:
        cafepass = None

    return cafepass