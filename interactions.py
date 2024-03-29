import ratcave.graphics as graphics
from ratcave.utils import timers
import random
import numpy as np

class Spinner(graphics.Physical):

    def __init__(self, spin_velocity=180., axis=1, *args, **kwargs):
        """Spins in direction "axis" with speed "velocity" when Spinner.update_physics(dt) is called!"""
        super(Spinner, self).__init__(*args, **kwargs)

        self.velocity = 0.
        self.spin_velocity = spin_velocity
        self.axis = axis
        self.timer = timers.countdown_timer(0)

    def start(self, *args, **kwargs):
        if self.velocity:
            self.timer = timers.countdown_timer(2.)
        else:
            self.velocity = self.spin_velocity * random.choice([1., -1.])


    def update(self, dt):
        # Keep spinning if timeout hasn't completed.
        if self.timer.next() > 0.:
            self.rot_y += self.velocity * dt


class Jumper(graphics.Physical):

    def __init__(self, jump_velocity=.6, gravity_coeff=-4.5, jump_count=3, *args, **kwargs):
        """Jumps with jump_velocity, coming back down at rate gravity_coeff."""
        super(Jumper, self).__init__(*args, **kwargs)

        self.floor_height = self.y
        self.gravity_coeff = gravity_coeff
        self.jump_velocity = jump_velocity
        self.jump_count = jump_count
        self.jumps_remaining = 0
        self.velocity = 0.

    def start(self, *args, **kwargs):

        # Reset to floor height (to prevent air-jumping)
        if not self.jumps_remaining:
            self.jumps_remaining = self.jump_count
        else:
            self.jumps_remaining -= 1

        if self.y <= self.floor_height:
            self.y = self.floor_height + .005
            self.velocity = self.jump_velocity

    def update(self, dt):

        # if in the air, update position via gravitational constant
        if self.y > self.floor_height:
            self.velocity += (self.gravity_coeff * dt)
            self.y += (self.velocity * dt)
            return
        elif self.y <= self.floor_height:
            self.velocity = 0
            if self.jumps_remaining > 0:
                self.start()
            else:
                self.y = self.floor_height
            return


class Scaler(graphics.Physical):

    def __init__(self, end_scale=.5, scale_velocity=.025, *args, **kwargs):
        """Grows and Shrinks between its scale and the end_scale (relative to its current scale) endpoints with speed scale_velocity."""

        super(Scaler, self).__init__(*args, **kwargs)
        self.scale_endpoints = tuple(sorted((self.scale, self.scale * end_scale)))
        self.scale_velocity = scale_velocity
        self.scale_direction = -1 if end_scale < self.scale else 1.
        self.timer = timers.countdown_timer(0)

    def start(self, *args, **kwargs):
        self.timer = timers.countdown_timer(2.)

    def update(self, dt):

        if self.timer.next() > 0.:

            # When it reaches the end of the scale range, flip the direction
            if self.scale < self.scale_endpoints[0] or self.scale > self.scale_endpoints[1]:
                self.scale_direction *= -1

            # Set New Scale
            self.scale += self.scale_direction * self.scale_velocity * dt

class Runner(graphics.Physical):

    def __init__(self, run_speed=.3, return_time=.3, *args, **kwargs):
        super(Runner, self).__init__(*args, **kwargs)
        self.run_speed = run_speed
        self.return_time = return_time
        self.timer = timers.countdown_timer(0)
        self.orig_x = self.x
        self.orig_z = self.z

        self.run_direction = 0., 0.

    def start(self, *args, **kwargs):
        # FIXME: Calculation of run directoin is completely wrong because of the local/world coordinate distinction
        if self.timer.next() < 0.02:
            run_direction = np.subtract(self.position, kwargs['from_obj'].position)[::2]  # Calculate direction away from from_obj
            self.run_direction = run_direction / np.linalg.norm(run_direction)  # Normalilze vector
            self.timer = timers.countdown_timer(self.return_time)

    def update(self, dt):
        if self.timer.next() > 0.:
            move_amt = np.dot(np.dot(self.run_direction, dt), self.run_speed).tolist()
            self.x += move_amt[0]
            self.z += move_amt[1]
        else:
            self.x, self.z = self.orig_x, self.orig_z

