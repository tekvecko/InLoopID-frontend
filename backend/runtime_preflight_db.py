from __future__ import annotations

from pathlib import Path
import os

from alembic.config import Config as AlembicConfig
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory

from app import app
from models import db


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "migrations"


def get_script_directory() -> ScriptDirectory:
    candidates = [
        MIGRATIONS / "alembic.ini",
        ROOT / "alembic.ini",
    ]

    config_file = next(
        (
            path
            for path in candidates
            if path.is_file()
        ),
        None,
    )

    if config_file is None:
        raise RuntimeError(
            "Alembic config file not found."
        )

    cfg = AlembicConfig(
        str(config_file)
    )

    cfg.set_main_option(
        "script_location",
        str(MIGRATIONS),
    )

    return ScriptDirectory.from_config(
        cfg
    )


def migration_gate(connection) -> None:
    script = get_script_directory()

    heads = tuple(
        script.get_heads()
    )

    if len(heads) != 1:
        raise RuntimeError(
            "Expected exactly one Alembic head, "
            f"got {heads!r}"
        )

    context = MigrationContext.configure(
        connection
    )

    current = tuple(
        context.get_current_heads()
    )

    print(
        "Alembic head    :",
        heads,
    )

    print(
        "Database current:",
        current,
    )

    if current != heads:
        raise RuntimeError(
            "Production database migration revision "
            "does not match Alembic head. "
            f"current={current!r}, head={heads!r}"
        )

    print(
        "[OK] ALEMBIC_CURRENT_EQUALS_HEAD"
    )


def sqlite_gate(connection) -> None:
    if connection.dialect.name != "sqlite":
        print(
            "[INFO] Non-SQLite database; "
            "SQLite PRAGMA checks skipped."
        )
        return

    foreign_keys = connection.exec_driver_sql(
        "PRAGMA foreign_keys"
    ).scalar()

    print(
        "PRAGMA foreign_keys:",
        foreign_keys,
    )

    if foreign_keys != 1:
        raise RuntimeError(
            "SQLite foreign key enforcement "
            "is disabled."
        )

    print(
        "[OK] SQLITE_FOREIGN_KEYS_ENABLED"
    )

    integrity = connection.exec_driver_sql(
        "PRAGMA integrity_check"
    ).fetchall()

    print(
        "PRAGMA integrity_check:",
        integrity,
    )

    if integrity != [("ok",)]:
        raise RuntimeError(
            "SQLite integrity_check failed: "
            f"{integrity!r}"
        )

    print(
        "[OK] SQLITE_INTEGRITY_OK"
    )

    violations = connection.exec_driver_sql(
        "PRAGMA foreign_key_check"
    ).fetchall()

    print(
        "PRAGMA foreign_key_check:",
        violations,
    )

    if violations:
        raise RuntimeError(
            "SQLite foreign key violations detected: "
            f"{violations!r}"
        )

    print(
        "[OK] SQLITE_FOREIGN_KEY_CHECK_OK"
    )



# INLOOPID_SIGNING_READINESS_GATE_V1
def signing_readiness_gate() -> None:
    if (
        os.getenv(
            "INLOOPID_REQUIRE_SIGNING_READY",
            "0",
        )
        != "1"
    ):
        print(
            "[INFO] Signing readiness gate disabled"
        )
        return

    issuer_did = (
        os.getenv(
            "ISSUER_DID",
            "",
        )
        .strip()
    )

    tenant_id = (
        os.getenv(
            "INLOOPID_ISSUER_TENANT",
            "",
        )
        .strip()
    )

    if not issuer_did:
        raise RuntimeError(
            "ISSUER_DID is required"
        )

    if not tenant_id:
        raise RuntimeError(
            "INLOOPID_ISSUER_TENANT is required"
        )

    from crypto_signing import (
        load_private_key,
        validate_identity_key,
    )
    from models import IdentityNode
    from tsa_service import (
        ca_file,
        tsa_url,
    )

    issuer = (
        IdentityNode.query
        .filter_by(
            did_uri=issuer_did,
            tenant_id=tenant_id,
            is_active=True,
        )
        .first()
    )

    if issuer is None:
        raise RuntimeError(
            "Configured active issuer identity "
            "was not found"
        )

    key = load_private_key()

    validate_identity_key(
        issuer,
        key,
    )

    tsa_url()
    ca_file()

    print(
        "[OK] ED25519_ISSUER_KEY_MATCH"
    )

    print(
        "[OK] TSA_CONFIG_READY"
    )

    print(
        "[OK] SIGNING_READINESS_GATE_PASS"
    )


def main() -> None:
    with app.app_context():
        with db.engine.connect() as connection:
            migration_gate(
                connection
            )

            sqlite_gate(
                connection
            )

        signing_readiness_gate()

    print(
        "[OK] DATABASE_PREFLIGHT_GATE_PASS"
    )


if __name__ == "__main__":
    main()
