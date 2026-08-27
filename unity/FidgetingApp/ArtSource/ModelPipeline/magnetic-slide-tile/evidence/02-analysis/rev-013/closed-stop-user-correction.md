# Gate 02 rev 13 user-authoritative closed stop

Date: 2026-08-26

DecisionState: requested correction; rev 12 mechanism principle partially accepted.

The top plate cannot travel below the fixed bottom plate. `s=0` is the exact
closed state at `θ=0°`, where both exterior capsule silhouettes coincide.
Allowed travel is `0 ≤ s ≤ sMax`. Any direct, keyboard, parameter, or API input
that requests `s<0` clamps to `0`.

At the closed stop, an inward pointer component cannot move the top through the
bottom. A simultaneous tangential component may still rotate the top and
carrier. This is a hard CAD kinematic limit only. It does not define bounce,
force, softness, damping, friction, or Haptic behavior.
