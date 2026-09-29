from engine import check, next_phase
from schema import Guard, GuardOp, Phase, Workflow

# Test tool is allowed or not in that phase
def test_allow_tool():
    # global workflow
    workflow = Workflow(
        id="test-workflow",
        initial="plan",
        phases={
            "plan": Phase(tools=["read", "grep"]),
        },
    )

    read_result = check("plan", "read", workflow, context={})
    grep_result = check("plan", "grep", workflow, context={})

    assert read_result["allowed"] is True
    assert grep_result["allowed"] is True

# Test tool is blocked by engine or not
def test_block_tool():
    # workflow
    workflow = Workflow(
        id="test-workflow",
        initial="plan",
        phases={
            "plan": Phase(tools=["read", "grep"]),
        },
    )

    result = check("plan", "edit", workflow, context={})
    assert result["allowed"] is False

# Test transtion of phase (plan --> implement)
def test_transition():
    # workflow for move plan to implement.
    workflow = Workflow(
        id="test-workflow",
        initial="plan",
        phases={
            "plan": Phase(tools=["read"], on={"READY": "implement"}),
            "implement": Phase(tools=["edit"]),
        },
    )

    # Ask the engine for the destination
    result = next_phase("plan", "READY", workflow)
    assert result == "implement"


# Test turn count, will it block or allow(in this case how many times agent can read a file)
def test_turn_count_guard():
    # The read tool is available only while turn_count is less than 2.
    workflow = Workflow(
        id="test-workflow",
        initial="plan",
        phases={
            "plan": Phase(
                tools=["read"],
                guards=[Guard(field="turn_count", op=GuardOp.less_than, value=2)],
            ),
        },
    )

    # count below
    allowed_result = check("plan", "read", workflow, context={"turn_count": 1})

    # count equal
    blocked_result = check("plan", "read", workflow, context={"turn_count": 2})

    assert allowed_result["allowed"] is True
    assert blocked_result["allowed"] is False
