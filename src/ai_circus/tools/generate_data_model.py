"""
generate_data_model.py
----------------------

Utility to generate a Pydantic Settings model from env_config.yaml.
Automates the synchronization of environment variable definitions
with the application's data model and .env.example file.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from loguru import logger

DEFAULT_CONFIG = "env_config.yaml"
DEFAULT_OUTPUT = "src/ai_circus/data_model.py"
DEFAULT_ENV_EXAMPLE = ".env.example"


def update_env_example(config: dict, output_path: str | Path) -> None:
    """Generate or update .env.example from config."""
    lines = []

    for var in config.get("env_variables", []):
        name = var["name"]
        description = var.get("description", "")
        default = var.get("default")

        if description:
            lines.append(f"# {description}")

        val_str = ""
        if default is not None:
            val_str = str(default)

        lines.append(f"{name}={val_str}")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")
    logger.info("Updated {}", output_path)


def generate_data_model(
    config_path: str | Path,
    output_path: str | Path,
    env_example_path: str | Path = DEFAULT_ENV_EXAMPLE,
) -> None:
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
        "from typing import Any",
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
        is_mandatory = var.get("mandatory", False)
        is_secret = var.get("secret", False)
        default = var.get("default")

        base_type = "SecretStr" if is_secret else "str"
        type_hint = base_type if is_mandatory else f"{base_type} | None"

        description = var.get("description", "").replace('"', '\\"')

        field_args = [f'description="{description}"']
        if not (is_mandatory and default is None):
            if default is None:
                field_args.append("default=None")
            elif isinstance(default, str):
                field_args.append(f'default="{default}"')
            else:
                field_args.append(f"default={default}")

        # format as multi-line if total length would be long
        line_start = f"    {name}: {type_hint} = Field("
        args_str = ", ".join(field_args)
        if len(line_start + args_str + ")") > 80:
            lines.append(line_start)
            for i, arg in enumerate(field_args):
                comma = "," if i < len(field_args) - 1 else ""
                lines.append(f"        {arg}{comma}")
            lines[-1] += "\n    )"
        else:
            lines.append(f"{line_start}{args_str})")

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
                "            raise ValueError(",
                f'                "{err}"',
                "            )",
                "        return v",
            ])

    lines.extend([
        "",
        "",
        "EnvConfig.model_rebuild()",
        "",
        "env_config = EnvConfig()",
        "",
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
        "",
        'if __name__ == "__main__":',
        "    main()",
    ])

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    logger.info("Generated {} from {}", output_path, config_path)
    update_env_example(config, env_example_path)


def main() -> None:
    """Entry point for the generator tool."""
    parser = argparse.ArgumentParser(description="Generate Pydantic model from YAML.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to env_config.yaml")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output path for data_model.py")
    parser.add_argument("--env-example", default=DEFAULT_ENV_EXAMPLE, help="Output path for .env.example")
    args = parser.parse_args()

    generate_data_model(args.config, args.output, args.env_example)


if __name__ == "__main__":
    main()
