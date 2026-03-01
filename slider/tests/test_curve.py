from math import isclose

from slider.curve import Catmull
from slider.position import Position


class TestCatmull:
    def test_two_point_endpoints(self):
        """Two-point Catmull degenerates to a line; endpoints should be exact."""
        points = [Position(100, 200), Position(300, 400)]
        curve = Catmull(points, req_length=100)

        start = curve(0)
        end = curve(1)

        assert isclose(start.x, 100, abs_tol=1e-6)
        assert isclose(start.y, 200, abs_tol=1e-6)
        assert isclose(end.x, 300, abs_tol=1e-6)
        assert isclose(end.y, 400, abs_tol=1e-6)

    def test_three_point_endpoints(self):
        """Three-point Catmull should start and end at the first and last points."""
        points = [Position(0, 0), Position(100, 200), Position(300, 100)]
        curve = Catmull(points, req_length=400)

        start = curve(0)
        end = curve(1)

        assert isclose(start.x, 0, abs_tol=1e-6)
        assert isclose(start.y, 0, abs_tol=1e-6)
        assert isclose(end.x, 300, abs_tol=1e-6)
        assert isclose(end.y, 100, abs_tol=1e-6)

    def test_three_point_midpoint_influenced_by_tangents(self):
        """The midpoint of a 3-point Catmull should be influenced by tangents
        derived from neighboring control points."""
        points = [Position(0, 0), Position(0, 200), Position(200, 200)]
        curve = Catmull(points, req_length=400)

        # t=0.25 is the midpoint of the first segment (between points 0 and 1)
        mid = curve(0.25)

        # The tangent at P1 = 0.5*(P2-P0) = (100, 100), which has an
        # x-component that pulls the curve slightly left at the midpoint.
        # Hermite at s=0.5: x = (s^3 - s^2)*T1.x = -0.125*100 = -12.5
        assert isclose(mid.x, -12.5, abs_tol=1e-6)
        assert isclose(mid.y, 100.0, abs_tol=1e-6)

    def test_single_point(self):
        """Single-point Catmull should return that point for any t."""
        points = [Position(42, 99)]
        curve = Catmull(points, req_length=0)

        for t in [0, 0.5, 1]:
            pos = curve(t)
            assert pos.x == 42
            assert pos.y == 99

    def test_many_points_endpoints(self):
        """Many-point Catmull should still hit first and last points."""
        points = [
            Position(0, 0),
            Position(50, 100),
            Position(150, 150),
            Position(250, 100),
            Position(300, 0),
        ]
        curve = Catmull(points, req_length=500)

        start = curve(0)
        end = curve(1)

        assert isclose(start.x, 0, abs_tol=1e-6)
        assert isclose(start.y, 0, abs_tol=1e-6)
        assert isclose(end.x, 300, abs_tol=1e-6)
        assert isclose(end.y, 0, abs_tol=1e-6)
