"""
Query-scoping regression guard
---------------------------------
This is not a runtime test — it's a static-analysis check that parses every
router's source with Python's `ast` module and flags any function that
queries an outlet-owned model (`db.query(Sale)`, `db.query(Inventory)`,
etc. — see app/core/scoping.SCOPED_MODELS) without also referencing
`scoped_outlet_ids(` or `apply_outlet_scope(` somewhere in that same
function body.

Why this exists: three separate rounds of manual code review each found a
*new* instance of "endpoint queries outlet-owned data, forgot to scope it"
across this codebase. A human remembering to check is not a reliable
control for this bug class at this codebase size. This test is the control
that replaces "remember to check" — it runs in CI/pytest with no DB and no
running server required, so it catches the mistake at commit time instead
of at "someone in another region reads data they shouldn't."

If you add a genuinely admin-only endpoint that intentionally queries a
scoped model without restriction (e.g. a network-wide dashboard only admins
can reach), add its function name to INTENTIONALLY_UNSCOPED below with a
one-line reason — don't just ignore a failure here.
"""
import ast
import os

ROUTERS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "routers")

SCOPED_MODEL_NAMES = {"Sale", "Customer", "Inventory", "Employee", "Audit", "MarketingCampaign", "Recommendation", "Alert", "AIInsight"}

SCOPE_MARKERS = {"scoped_outlet_ids", "apply_outlet_scope", "_assert_outlet_access"}

# Function name -> reason it's allowed to query a scoped model without
# calling scoped_outlet_ids/apply_outlet_scope in its own body. Keep this
# list short and each entry justified — it's meant to be a speed bump, not
# a rubber stamp.
INTENTIONALLY_UNSCOPED: dict[str, str] = {
    # Helper that BUILDS the scope itself — nothing to scope against yet.
    "get_outlet_or_404": "computes scope internally via scoped_outlet_ids inside outlet_service, not this file",
}


def _function_queries_scoped_model(func_node: ast.FunctionDef) -> set[str]:
    """Returns the set of scoped model names this function calls db.query(...) on."""
    found = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "query":
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in SCOPED_MODEL_NAMES:
                    found.add(arg.id)
    return found


def _function_references_scope_marker(func_node: ast.FunctionDef, source: str) -> bool:
    func_source = ast.get_source_segment(source, func_node) or ""
    return any(marker in func_source for marker in SCOPE_MARKERS)


def _iter_router_files():
    for filename in sorted(os.listdir(ROUTERS_DIR)):
        if filename.endswith(".py") and filename != "__init__.py":
            yield os.path.join(ROUTERS_DIR, filename)


def test_every_scoped_model_query_is_scoped_or_allowlisted():
    violations = []

    for filepath in _iter_router_files():
        source = open(filepath).read()
        tree = ast.parse(source, filename=filepath)

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            queried_models = _function_queries_scoped_model(node)
            if not queried_models:
                continue

            if node.name in INTENTIONALLY_UNSCOPED:
                continue

            if not _function_references_scope_marker(node, source):
                violations.append(
                    f"{os.path.basename(filepath)}:{node.lineno} function '{node.name}' "
                    f"queries {sorted(queried_models)} without calling scoped_outlet_ids()/apply_outlet_scope() "
                    f"anywhere in its body, and isn't in INTENTIONALLY_UNSCOPED."
                )

    assert not violations, (
        "Found endpoint(s) querying outlet-owned data without scoping — this is exactly the bug class "
        "that caused real data leaks earlier in this project. Fix the endpoint, or if it's genuinely "
        "meant to be unrestricted, add it to INTENTIONALLY_UNSCOPED in this test file with a reason.\n\n"
        + "\n".join(violations)
    )


def test_scoped_models_registry_matches_models_with_outlet_id_column():
    """
    Sanity check on the registry itself: every model that actually has an
    outlet_id column should be in SCOPED_MODEL_NAMES, so a newly-added
    outlet-owned model doesn't silently fall outside this guard's coverage.
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
    from app.core.scoping import SCOPED_MODELS

    assert set(SCOPED_MODELS.keys()) == SCOPED_MODEL_NAMES, (
        "app/core/scoping.py's SCOPED_MODELS and this test's SCOPED_MODEL_NAMES have drifted apart — "
        "keep them in sync."
    )
