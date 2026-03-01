from math import isclose

from slider.curve import Catmull
from slider.position import Position


class TestCatmull:
    def test_single_point(self):
        """Single-point Catmull should return that point for any t."""
        curve = Catmull([Position(42, 99)], req_length=0)

        for t in [0, 0.5, 1]:
            pos = curve(t)
            assert pos.x == 42
            assert pos.y == 99

    def test_endpoints(self):
        """Catmull curves should start at the first point and end at the last."""
        cases = [
            [Position(100, 200), Position(300, 400)],
            [Position(0, 0), Position(100, 200), Position(300, 100)],
            [Position(0, 0), Position(50, 100), Position(150, 150),
             Position(250, 100), Position(300, 0)],
        ]

        for pts in cases:
            curve = Catmull(pts, req_length=500)
            start = curve(0)
            end = curve(1)

            assert isclose(start.x, pts[0].x, abs_tol=1e-6)
            assert isclose(start.y, pts[0].y, abs_tol=1e-6)
            assert isclose(end.x, pts[-1].x, abs_tol=1e-6)
            assert isclose(end.y, pts[-1].y, abs_tol=1e-6)

    def test_two_point_midpoint(self):
        """Two-point Catmull midpoint should be biased toward the start,
        matching osu's extrapolated boundary condition."""
        curve = Catmull([Position(0, 0), Position(200, 0)], req_length=200)
        mid = curve(0.5)

        # With osu's extrapolation, the midpoint is pulled toward the start
        assert isclose(mid.x, 87.5, abs_tol=1e-6)
        assert isclose(mid.y, 0, abs_tol=1e-6)

    def test_three_point_segment_continuity(self):
        """Adjacent segments should meet at the shared control point."""
        curve = Catmull(
            [Position(0, 0), Position(100, 200), Position(300, 100)],
            req_length=400,
        )

        # t=0.5 is the boundary between segment 0 and segment 1
        # Both segments should evaluate to the middle control point
        pos = curve(0.5)
        assert isclose(pos.x, 100, abs_tol=1e-6)
        assert isclose(pos.y, 200, abs_tol=1e-6)
