"""Maps song time to scenes."""
from types import SimpleNamespace
from clock import Clock
import engine


def build():
    ctx = SimpleNamespace(clock=Clock(), timeline=engine.Timeline(), scenes={})
    tl = ctx.timeline
    import sc_intro, sc_chant, sc_v1, sc_pre, sc_chorus
    S = ctx.scenes
    S["chant"] = sc_chant.ChantScene(ctx, 1)
    S["fog_lift"] = sc_pre.PreChorus(ctx, 3, lift=(0, 1))
    intro = sc_intro.Intro(ctx, 0)
    intro.next_scene = S["chant"]
    cuts = [(0.0, intro),
            (tl.sec(1)["start"] - 2.0, S["chant"]),
            (tl.sec(2)["start"], sc_v1.Verse1(ctx, 2)),
            (tl.sec(3)["start"], sc_pre.PreChorus(ctx, 3)),
            (tl.sec(4)["start"], sc_chorus.Chorus(ctx, 4))]
    return ctx, cuts


class Director:
    def __init__(self):
        self.ctx, self.cuts = build()

    def frame(self, t):
        scene = self.cuts[0][1]
        for st, sc in self.cuts:
            if t >= st:
                scene = sc
        return scene.frame(t)
