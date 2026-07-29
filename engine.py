from schema import GuardOp

# guard is the rule we defind in yaml and context come from session of agent
# like [guard --> turn_count, less_than, 8]   [context, turn_count is 9]  this fxn will return false--> block
def eval_guard(guard, context):
    field_value = context.get(guard.field)

    if guard.op == GuardOp.exists:
        return field_value is not None
    if guard.op == GuardOp.not_exists:
        return field_value is None

    if field_value is None:
        if guard.op in (GuardOp.less_than, GuardOp.less_than_equal, GuardOp.greater_than, GuardOp.greater_than_equal, GuardOp.equal, GuardOp.not_equal):
            field_value = 0
        else:
            return False

    if guard.op == GuardOp.equal:
        return field_value == guard.value
    if guard.op == GuardOp.not_equal:
        return field_value != guard.value
    if guard.op == GuardOp.greater_than:
        return field_value > guard.value
    if guard.op == GuardOp.greater_than_equal:
        return field_value >= guard.value
    if guard.op == GuardOp.less_than:
        return field_value < guard.value
    if guard.op == GuardOp.less_than_equal:
        return field_value <= guard.value
    if guard.op == GuardOp.in_:
        return field_value in guard.value
    if guard.op == GuardOp.contains:
        return str(guard.value) in str(field_value)

    return False

def check(phase_name, tool, workflow, context):
    phase = workflow.phases[phase_name]

    if tool not in phase.tools:
        transitions = list(phase.on.keys())
        transition_hint = ""
        if transitions:
            transition_hint = f"\nTo advance: call kitsune_transition with trigger: {', '.join(transitions)}"
        return {
            "allowed": False,
            "reason": f"Tool '{tool}' not available in phase '{phase_name}'",
            "current_phase": phase_name,
            "next_phase": None,
            "available_tools": phase.tools,
            "available_transitions": transitions,
            "message": f"🦊 [Kitsune] Tool '{tool}' not available in phase '{phase_name}'. Allowed: {', '.join(phase.tools)}.{transition_hint}",
        }

    # for each guards means like turn_count or max_count check that compare to session context does it allow or block using
    # eval_guard
    for guard in phase.guards:
       if not eval_guard(guard, context):
            transitions = list(phase.on.keys())
            transition_hint = ""
            if transitions:
                transition_hint = f"\nTo advance: call kitsune_transition with trigger: {', '.join(transitions)}"
            return {
                "allowed": False,
                "reason": guard.message or f"Guard failed: {guard.field} {guard.op.value} {guard.value}",
                "current_phase": phase_name,
                "next_phase": None,
                "available_tools": phase.tools,
                "available_transitions": transitions,
                "message": f"🦊 [Kitsune] {guard.message or f'Guard failed: {guard.field} {guard.op.value} {guard.value}'}.{transition_hint}",
            }

    # for specific tool only
    for guard in phase.tool_guards.get(tool, []):
       if not  eval_guard(guard, context):
            transitions = list(phase.on.keys())
            transition_hint = ""
            if transitions:
                transition_hint = f"\nTo advance: call kitsune_transition with trigger: {', '.join(transitions)}"
            return {
                "allowed": False,
                "reason": guard.message or f"Guard failed: {guard.field} {guard.op.value} {guard.value}",
                "current_phase": phase_name,
                "next_phase": None,
                "available_tools": phase.tools,
                "available_transitions": transitions,
                "message": f"🦊 [Kitsune] {guard.message or f'Guard failed: {guard.field} {guard.op.value} {guard.value}'}.{transition_hint}",
            }

    return {
        "allowed": True,
        "reason": None,
        "current_phase": phase_name,
        "next_phase": None,
        "available_tools": phase.tools,
        "available_transitions": list(phase.on.keys()),
        "message": "🦊 [Kitsune] Tool allowed",
    }

def next_phase(phase_name, trigger, workflow):
    phase = workflow.phases[phase_name]
    return phase.on.get(trigger)
