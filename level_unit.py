import MGUI
import math


# Unit states
state_idle = "idle"
state_walk = "walk"
state_battle = "battle"
state_fade = "fade"
state_delete = "delete"


class Unit(MGUI.AnimSprite):
    def __init__(self, x, y, player_owned, unit_data=None):
        super().__init__(0, 0, 1, 1)
        # Draw position is relative to the level canvas
        self.draw_x = 0
        self.draw_y = 0
        self.state = "walk"
        self.battle_target = None

        self.speed = 0
        self.player_owned = player_owned

        self.maxhp = 1
        self.hp = self.maxhp
        self.dmg_phys = 1
        self.attspd = 1
        self.att_ticker = 0

        if unit_data:
            self.load_unit(unit_data)

        self.healthbar = MGUI.Healthbar(0, self.get_height() - 2, self.get_width(), 2)
        self.healthbar.set_background((20, 20, 20))
        self.healthbar.set_color((100, 255, 100))

        # Center draw position to assigned tile
        unit_x = 32 + x * 48 - math.floor(self.get_width() / 2)
        unit_y = 42 + y * 48 - self.get_height()
        self.set_draw_position(unit_x, unit_y)

    def load_unit(self, unit_data):
        for attr in unit_data:
            if attr == "img_data":  # Load animated sprite data
                anim_data = unit_data[attr]
                self.set_icon_animated("assets/units/" + anim_data["img"], anim_data["frames"])
                if "anim_delay" in anim_data:
                    self.set_animation_delay(anim_data["anim_delay"])
                if "anim_order" in anim_data:
                    self.set_animation_order(anim_data["anim_order"])
                if "rotate" in anim_data:
                    self.set_rotation(anim_data["rotate"])
                flip_hor = "flip_hor" in anim_data
                # Flip enemy units horizontally
                flip_hor = flip_hor and self.player_owned or not flip_hor and not self.player_owned
                flip_ver = "flip_ver" in anim_data
                if flip_hor or flip_ver:
                    self.set_flip(flip_hor, flip_ver)
            elif hasattr(self, attr):
                setattr(self, attr, unit_data[attr])
        self.hp = self.maxhp
        self.attspd = math.ceil(self.attspd * 60)

    def set_draw_position(self, x, y):
        self.draw_x = x
        self.draw_y = y

    def get_draw_position(self):
        return self.draw_x, self.draw_y

    def hurt(self, dmg, dmg_type=None):
        self.hp -= dmg  # TODO handle damage types

    # Target can be building or unit
    def set_battle_target(self, target):
        if target:
            self.state = state_battle
            self.battle_target = target

    def tick(self):
        # Death
        if self.hp <= 0:
            self.state = state_fade
        else:
            # Handle healthbar
            if self.hp < self.maxhp:
                self.healthbar.set_visible(True)
                self.healthbar.set_percentage(self.hp / max(1, self.maxhp))
            else:
                self.healthbar.set_visible(False)

        # Walking state
        if self.state == state_walk:
            mx, my = self.get_draw_position()
            if self.player_owned:
                mx += self.speed
            else:
                mx -= self.speed
            self.set_draw_position(mx, my)
        # Battle state
        elif self.state == state_battle:
            if self.att_ticker > 0:
                self.att_ticker -= 1
            else:
                if self.battle_target:
                    dmg = self.dmg_phys  # TODO add other damage types when necessary
                    self.battle_target.hurt(dmg)
                    if self.battle_target.hp <= 0:
                        self.battle_target = None
                    self.att_ticker = self.attspd
                else:
                    self.state = state_walk

        # Fading state (out of bounds)
        elif self.state == state_fade:
            tmp_alpha = self.get_alpha()
            if tmp_alpha > 0:
                self.set_alpha(tmp_alpha - 15)
            else:
                self.state = state_delete

    def _get_appearance(self, *args):
        surface = super()._get_appearance(*args)
        if self.healthbar.is_visible():
            surface.blit(self.healthbar._get_appearance(*args), self.healthbar.get_position())
        return surface