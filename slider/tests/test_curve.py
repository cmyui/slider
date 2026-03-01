from math import isclose

from slider.curve import Catmull
from slider.position import Position


def _osu_catmull_rom(v1, v2, v3, v4, t):
    """Reference implementation matching osu-stable's Vector2.CatmullRom."""
    t2 = t * t
    t3 = t2 * t
    x = 0.5 * (2*v2[0] + (-v1[0]+v3[0])*t + (2*v1[0]-5*v2[0]+4*v3[0]-v4[0])*t2 + (-v1[0]+3*v2[0]-3*v3[0]+v4[0])*t3)
    y = 0.5 * (2*v2[1] + (-v1[1]+v3[1])*t + (2*v1[1]-5*v2[1]+4*v3[1]-v4[1])*t2 + (-v1[1]+3*v2[1]-3*v3[1]+v4[1])*t3)
    return x, y


def _osu_catmull_points(points, segment):
    """Pick 4 control points matching osu-stable's SliderOsu boundary logic.

    For each segment j, osu picks:
      v1 = points[j-1]   (clamped to points[j] when j==0)
      v2 = points[j]
      v3 = points[j+1]   (extrapolated as v2+(v2-v1) when out of range)
      v4 = points[j+2]   (extrapolated as v3+(v3-v2) when out of range)
    """
    j = segment
    n = len(points)
    v1 = points[j - 1] if j - 1 >= 0 else points[j]
    v2 = points[j]
    if j + 1 < n:
        v3 = points[j + 1]
    else:
        v3 = (v2[0] + (v2[0] - v1[0]), v2[1] + (v2[1] - v1[1]))
    if j + 2 < n:
        v4 = points[j + 2]
    else:
        v4 = (v3[0] + (v3[0] - v2[0]), v3[1] + (v3[1] - v2[1]))
    return v1, v2, v3, v4


class TestCatmull:
    def test_two_point_matches_osu(self):
        """Two-point Catmull should match osu-stable's evaluation."""
        points = [Position(100, 200), Position(300, 400)]
        curve = Catmull(points, req_length=100)
        pts = [(100, 200), (300, 400)]

        for t_local in [0, 0.25, 0.5, 0.75, 1.0]:
            t_global = t_local
            v1, v2, v3, v4 = _osu_catmull_points(pts, 0)
            expected = _osu_catmull_rom(v1, v2, v3, v4, t_local)
            result = curve(t_global)
            assert isclose(result.x, expected[0], abs_tol=1e-6), \
                f"t={t_global}: x={result.x} != {expected[0]}"
            assert isclose(result.y, expected[1], abs_tol=1e-6), \
                f"t={t_global}: y={result.y} != {expected[1]}"

    def test_three_point_matches_osu(self):
        """Three-point Catmull should match osu-stable's evaluation."""
        points = [Position(0, 0), Position(100, 200), Position(300, 100)]
        curve = Catmull(points, req_length=400)
        pts = [(0, 0), (100, 200), (300, 100)]

        for seg in range(2):
            v1, v2, v3, v4 = _osu_catmull_points(pts, seg)
            for t_local in [0, 0.25, 0.5, 0.75, 1.0]:
                t_global = (seg + t_local) / 2
                expected = _osu_catmull_rom(v1, v2, v3, v4, t_local)
                result = curve(t_global)
                assert isclose(result.x, expected[0], abs_tol=1e-6), \
                    f"seg{seg} t_local={t_local}: x={result.x} != {expected[0]}"
                assert isclose(result.y, expected[1], abs_tol=1e-6), \
                    f"seg{seg} t_local={t_local}: y={result.y} != {expected[1]}"

    def test_five_point_matches_osu(self):
        """Five-point Catmull should match osu-stable's evaluation."""
        points = [
            Position(0, 0),
            Position(50, 100),
            Position(150, 150),
            Position(250, 100),
            Position(300, 0),
        ]
        curve = Catmull(points, req_length=500)
        pts = [(0, 0), (50, 100), (150, 150), (250, 100), (300, 0)]
        n_segments = 4

        for seg in range(n_segments):
            v1, v2, v3, v4 = _osu_catmull_points(pts, seg)
            for t_local in [0, 0.25, 0.5, 0.75, 1.0]:
                t_global = (seg + t_local) / n_segments
                expected = _osu_catmull_rom(v1, v2, v3, v4, t_local)
                result = curve(t_global)
                assert isclose(result.x, expected[0], abs_tol=1e-6), \
                    f"seg{seg} t_local={t_local}: x={result.x} != {expected[0]}"
                assert isclose(result.y, expected[1], abs_tol=1e-6), \
                    f"seg{seg} t_local={t_local}: y={result.y} != {expected[1]}"

    def test_single_point(self):
        """Single-point Catmull should return that point for any t."""
        points = [Position(42, 99)]
        curve = Catmull(points, req_length=0)

        for t in [0, 0.5, 1]:
            pos = curve(t)
            assert pos.x == 42
            assert pos.y == 99

    def test_endpoints(self):
        """Catmull curves should start at the first point and end at the last."""
        for pts in [
            [Position(100, 200), Position(300, 400)],
            [Position(0, 0), Position(100, 200), Position(300, 100)],
            [Position(0, 0), Position(50, 100), Position(150, 150),
             Position(250, 100), Position(300, 0)],
        ]:
            curve = Catmull(pts, req_length=500)
            start = curve(0)
            end = curve(1)
            assert isclose(start.x, pts[0].x, abs_tol=1e-6), \
                f"{len(pts)}-point: start.x={start.x} != {pts[0].x}"
            assert isclose(start.y, pts[0].y, abs_tol=1e-6)
            assert isclose(end.x, pts[-1].x, abs_tol=1e-6), \
                f"{len(pts)}-point: end.x={end.x} != {pts[-1].x}"
            assert isclose(end.y, pts[-1].y, abs_tol=1e-6)
