"""
generate_data_model.py
----------------------

Utility to generate a Pydantic Settings model from env_config.yaml.
Automates the synchronization of environment variable definitions
with the application's data model.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from loguru import logger

DEFAULT_CONFIG = "env_config.yaml"
DEFAULT_OUTPUT = "src/ai_circus/data_model.py"


def generate_data_model(config_path: str | Path, output_path: str | Path) -> None:
    """Read YAML config and write the Pydantic model file."""
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    global_settings = config.get("global_settings", {})
    env_file = global_settings.get("env_file", ".env")
    case_sensitive = global_settings.get("case_sensitive", True)

    lines = [
        '"""',
        "data_model.py",
        "-----------",
        "Generated Pydantic Settings model from env_config.yaml.",
        "DO NOT EDIT DIRECTLY. Run 'make generate' to update.",
        "",
        "Author: Angel Martinez-Tenor, 2026.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import re",
        "from typing import Any, Optional",
        "",
        "from pydantic import Field, SecretStr, field_validator",
        "from pydantic_settings import BaseSettings, SettingsConfigDict",
        "",
        "",
        "class EnvConfig(BaseSettings):",
        '    """Environment configuration model."""',
        "",
        "    model_config = SettingsConfigDict(",
        f'        env_file="{env_file}",',
        '        env_file_encoding="utf-8",',
        '        extra="ignore",',
        f"        case_sensitive={case_sensitive},",
        "    )",
    ]

    vars_list = config.get("env_variables", [])
    for var in vars_list:
        name = var["name"]
        type_hint = "str"
        if var.get("secret"):
            type_hint = "SecretStr"

        if not var.get("mandatory"):
            type_hint = f"Optional[{type_hint}]"

        default = var.get("default")
        if default is None:
            default_str = "None"
        elif isinstance(default, str):
            default_str = f'"{default}"'
        else:
            default_str = str(default)

        description = var.get("description", "").replace('"', '\\"')

        line = f"    {name}: {type_hint} = Field("
        line += f'default={default_str}, description="{description}"'
        line += ")  # noqa: E501"
        lines.append(line)

    # Add validators
    for var in vars_list:
        if "validation" in var and "regex" in var["validation"]:
            name = var["name"]
            regex = var["validation"]["regex"]
            err = var["validation"].get("error_message", f"Invalid format for {var['name']}").replace('"', '\\"')
            validator_name = f"validate_{name.lower()}"

            lines.extend([
                "",
                f'    @field_validator("{name}", mode="after")',
                "    @classmethod",
                f"    def {validator_name}(cls, v: Any) -> Any:",
                '        """Validate field format via regex."""',
                "        if v is None:",
                "            return v",
                "        val = v.get_secret_value() if hasattr(v, 'get_secret_value') else str(v)",
                f'        if not re.match(r"{regex}", val):',
                f'            raise ValueError("{err}")  # noqa: E501',
                "        return v",
            ])

    lines.extend([
        "",
        "EnvConfig.model_rebuild()",
        "",
        "env_config = EnvConfig()",
        "",
        "def main() -> None:",
        '    """Display the loaded configuration (redacted)."""',
        '    print("--- Loaded Configuration ---")  # noqa: T201',
        "    for field in EnvConfig.model_fields:",
        "        val = getattr(env_config, field)",
        '        if hasattr(val, "get_secret_value"):',
        '            val = "****" + val.get_secret_value()[-4:] if val and val.get_secret_value() else "None"',
        '        print(f"{field}: {val}")  # noqa: T201',
        "",
        'if __name__ == "__main__":',
        "    main()",
    ])

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    logger.info("Generated {} from {}", output_path, config_path)


def main() -> None:
    """Entry point for the generator tool."""
    parser = argparse.ArgumentParser(description="Generate Pydantic model from YAML.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to env_config.yaml")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output path for data_model.py")
    args = parser.parse_args()

    generate_data_model(args.config, args.output)


if __name__ == "__main__":
    main()
