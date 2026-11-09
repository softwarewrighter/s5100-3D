# Shared hardware modeling workflow

Use the shared `less-wrong-3d` skill in [../lucy-3D/skills/less-wrong-3d/SKILL.md](../lucy-3D/skills/less-wrong-3d/SKILL.md) when refining geometry, matching references, or validating renders.

Shared controls and process helpers live in `../lucy-3D/shared` and `../lucy-3D/scripts`. `just render` generates the viewer from that source. Do not add another keyboard listener or fork the common controls. Keep 5100-specific geometry here. See `../lucy-3D/docs/survey.md` for missing build dependencies and fidelity limitations.
