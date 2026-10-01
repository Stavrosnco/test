"""Maps song time to scenes."""
from types import SimpleNamespace
from clock import Clock
import engine


def build():
    ctx = SimpleNamespace(clock=Clock(), timeline=engine.Timeline(), scenes={})
    tl = ctx.timeline
    import sc_intro, sc_chant, sc_v1, sc_pre, sc_chorus, sc_v2, sc_v3, sc_v4, sc_v5, sc_bridge, sc_finale, sc_outro
    S = ctx.scenes
    S["chant"] = sc_chant.ChantScene(ctx, 1)
    S["fog_lift"] = sc_pre.PreChorus(ctx, 3, lift=(0, 1))
    S["v2"], S["v3"], S["v4"], S["v5"] = sc_v2.Verse2(ctx, 5), sc_v3.Verse3(ctx, 6), sc_v4.Verse4(ctx, 7), sc_v5.Verse5(ctx, 9)
    intro = sc_intro.Intro(ctx, 0)
    intro.next_scene = S["chant"]
    cuts = [(0.0, intro),
            (tl.sec(1)["start"] - 2.0, S["chant"]),
            (tl.sec(2)["start"], sc_v1.Verse1(ctx, 2)),
            (tl.sec(3)["start"], sc_pre.PreChorus(ctx, 3)),
            (tl.sec(4)["start"], sc_chorus.Chorus(ctx, 4)),
            (tl.sec(5)["start"], S["v2"]),
            (tl.sec(6)["start"], S["v3"]),
            (tl.sec(7)["start"], S["v4"]),
            (tl.sec(8)["start"], sc_chorus.Chorus(ctx, 8)),
            (tl.sec(9)["start"], S["v5"]),
            (tl.sec(10)["start"], sc_bridge.Bridge(ctx, 10)),
            (tl.sec(11)["start"], sc_finale.Finale(ctx, 11)),
            (tl.sec(12)["start"], sc_outro.Outro(ctx, 12))]
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
