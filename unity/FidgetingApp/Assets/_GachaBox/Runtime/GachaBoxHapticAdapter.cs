using CodexUnityLab;

namespace FidgetingApp.GachaBox
{
    /// <summary>
    /// Routes blind-box semantic events into the shared haptic router. This
    /// is the only bridge between the box state machine and rendering, and it
    /// only consumes semantic events — never raw input. A LidOpened weight of
    /// zero (skip/programmatic staging) stays silent by product rule.
    /// </summary>
    public static class GachaBoxHapticAdapter
    {
        public static void Route(GachaBoxEvent boxEvent)
        {
            switch (boxEvent.Kind)
            {
                case GachaBoxEventKind.RattleImpulse:
                    FidgetHapticRouter.Emit(
                        FidgetSemanticEvent.Collision,
                        boxEvent.Weight);
                    break;
                case GachaBoxEventKind.Warmed:
                    FidgetHapticRouter.Emit(
                        FidgetSemanticEvent.Pop,
                        boxEvent.Weight);
                    break;
                case GachaBoxEventKind.LidBreakaway:
                    FidgetHapticRouter.Emit(
                        FidgetSemanticEvent.Breakaway,
                        boxEvent.Weight);
                    break;
                case GachaBoxEventKind.LidOpened:
                    if (boxEvent.Weight > 0f)
                    {
                        FidgetHapticRouter.Emit(
                            FidgetSemanticEvent.Released,
                            boxEvent.Weight);
                    }

                    break;
            }
        }
    }
}
