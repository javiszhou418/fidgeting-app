# Gate 02 rev 15 user-authoritative minimum overlap disk

Date: 2026-08-27

DecisionState: Gate 02 rev 14 rejected. The finite groove model remains a
candidate travel bound, but pivot-point coverage and sparse sweep validation
are insufficient.

The red circle in the attached CAD screenshot is `MinimumOverlapDisk`. It is
fixed to `BottomBase`, centered on `FixedAxis`, and is distinct from both the
axis point and the bottom exterior outline. `TopPlate` must fully contain this
disk for every valid slide and rotation pose. Boundary contact is the legal
limit. Any exposed disk area is invalid.

Actual travel is the minimum of the finite-groove endpoint limit and the
geometric disk-containment limit. Physical disk radius, clearance, groove
length, and millimetre cover margin remain unknown. The reviewed red-circle
size is retained as a normalized CAD parameter only.
