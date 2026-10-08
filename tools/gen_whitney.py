#!/usr/bin/env python3
"""Generate assets/whitney.svg - a Whitney umbrella turning about its
singular line.

    f(u, v) = (u v, u, v^2)          implicitly   x^2 = y^2 z

The real variety has three pieces worth drawing:
  * the canopy, the image of f, which lies over z >= 0;
  * the double line, the positive z-axis, where the two sheets x = +-y sqrt(z)
    cross - every point of it is the image of two parameter points (0, +-v);
  * the handle, the negative z-axis, where x = y = 0 are the only real
    solutions, so the variety degenerates to a bare whisker.
The pinch point at the origin is the Whitney singularity itself.

How the rotation is done without JavaScript (the site ships
Content-Security-Policy script-src 'none'):

The umbrella is a RULED surface. The ruling v = const is the straight segment
{(u v, u, v^2) : u in [-A, A]}, which lies wholly inside the horizontal plane
z = v^2 and is centred on the axis. Under a rotation about the z-axis each
such plane maps to itself, and an orthographic projection restricted to one
horizontal plane is affine - precisely

    screen = translate(0, -z cos phi) . scale(1, -sin phi) . rotate(theta)

applied to the ruling's in-plane coordinates. So the turn is an exact CSS
rotation, not a flip-book of precomputed frames: one shared @keyframes drives
every ruling, and the per-ruling part (its height) is a static declaration.

The order matters. CSS composes the individual transform properties as
translate -> rotate -> scale -> transform, so putting the turn in `transform`
and leaving `rotate` unset yields translate . scale . transform, which is the
chain above. Each ruling is symmetric about its point of the axis, so
`transform-box: fill-box; transform-origin: center` pins the rotation to that
point exactly - do not swap this for a viewBox-relative origin.

The double line, the handle and the pinch point all lie on the axis, so they
are invariant under the rotation and are emitted as static geometry.
"""
import math
import sys

A      = 1.00                  # u runs over [-A, A]: half-width of the canopy
B      = 1.05                  # v runs over [-B, B]: z reaches B^2
PHI    = math.radians(40)      # camera elevation above the horizontal plane
NR     = 49                    # rulings drawn
HANDLE = 0.78                  # how far the whisker extends below the origin
TURN   = 18.0                  # seconds for a full revolution
S      = 100.0                 # world units -> SVG user units
PAD    = 18

sp, cp = math.sin(PHI), math.cos(PHI)


def f(x):
    s = f"{x:.1f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


# ------------------------------------------------------------------- rulings
# Drawn in plane coordinates, from u = -A to u = +A, so the segment is centred
# on the axis; CSS then lifts it to z = v^2 and turns it.
lines = []
for i in range(NR):
    v = -B + 2 * B * i / (NR - 1)
    px, py = A * v * S, A * S
    lift = -v * v * cp * S
    lines.append(f'  <path class="r" style="translate:0 {f(lift)}px" '
                 f'd="M{f(-px)} {f(-py)}L{f(px)} {f(py)}"/>')

# --------------------------------------------------------- the axis, at rest
ZTOP = B * B * cp * S
axis = (f'  <path class="handle" d="M0 0V{f(HANDLE * cp * S)}"/>\n'
        f'  <path class="double" d="M0 0V{f(-ZTOP)}"/>\n'
        f'  <circle class="pinch" cx="0" cy="0" r="3.4"/>')

# -------------------------------------------------------------------- canvas
rmax = A * math.sqrt(B * B + 1) * S          # largest distance from the axis
minx, maxx = -rmax, rmax
miny = -(sp * rmax + ZTOP)
maxy = max(A * sp * S, HANDLE * cp * S)
vb = (f"{f(minx - PAD)} {f(miny - PAD)} "
      f"{f(maxx - minx + 2 * PAD)} {f(maxy - miny + 2 * PAD)}")

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"
     role="img" aria-labelledby="wu-title wu-desc">
  <title id="wu-title">A Whitney umbrella turning about its singular line</title>
  <desc id="wu-desc">The surface x squared equals y squared times z, drawn
    through its straight-line rulings. The rulings cross in pairs along the
    vertical axis, which is therefore a double line; it is pinched to a single
    point at the origin, below which the surface degenerates to a bare
    whisker. The figure turns slowly about that axis.</desc>
  <style>
    .r {{
      fill: none;
      stroke: #2a6db0;
      stroke-width: 1.15;
      opacity: .42;
      transform-box: fill-box;      /* pin the turn to the ruling's midpoint, */
      transform-origin: center;     /* which is its point of the axis         */
      scale: 1 {-sp:.5f};
      animation: wu-turn {TURN:g}s linear infinite;
    }}
    @keyframes wu-turn {{
      from {{ transform: rotate(0deg); }}
      to   {{ transform: rotate(360deg); }}
    }}

    .double {{ fill: none; stroke: #c0442c; stroke-width: 2.8;
              stroke-linecap: round; }}
    .handle {{ fill: none; stroke: #78838f; stroke-width: 1.8;
              stroke-dasharray: 1 5.5; stroke-linecap: round; }}
    .pinch  {{ fill: #c0442c; }}

    @media (prefers-color-scheme: dark) {{
      .r      {{ stroke: #7fb4e6; opacity: .36; }}
      .double {{ stroke: #e8795f; }}
      .handle {{ stroke: #8592a0; }}
      .pinch  {{ fill: #e8795f; }}
    }}

    /* Accessibility: hold the umbrella still. */
    @media (prefers-reduced-motion: reduce) {{
      .r {{ animation: none; }}
    }}
  </style>

{chr(10).join(lines)}

{axis}
</svg>
"""

sys.stdout.write(svg)
