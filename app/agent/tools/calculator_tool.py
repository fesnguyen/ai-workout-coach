from __future__ import annotations

import ast
import operator

from app.agent.tools.base_tool import BaseTool


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculatorTool(BaseTool):
    """Safely evaluates simple arithmetic expressions."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def openai_definition(self) -> dict:
        return {
            "type": "function",
            "name": self.name,
            "description": "Evaluate a mathematical expression. \nUse this tool whenever arithmetic or numeric calculation is required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression such as '(12 + 5) * 3'.",
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
            "strict": True,
        }

    async def invoke(
        self,
        arguments: dict[str, object],
    ) -> str:
        expression = str(arguments.get("expression", "")).strip()

        if not expression:
            return "Error: Missing expression."

        try:
            tree = ast.parse(expression, mode="eval")
            result = self._evaluate(tree.body)
            return str(result)
        except Exception:
            return "Error: Invalid mathematical expression."

    def _evaluate(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError

        if isinstance(node, ast.BinOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError

            return op(
                self._evaluate(node.left),
                self._evaluate(node.right),
            )

        if isinstance(node, ast.UnaryOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError

            return op(self._evaluate(node.operand))

        raise ValueError
