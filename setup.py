import os
import sys
import xml.etree.ElementTree as ET
import aiosqlite

from pathlib import Path

import resources.const.glob as glob
from model.types.run_mode import RunMode, RunModeSettings
from resources.sql import scripts


def define_run_mode() -> RunMode:
    if len(sys.argv) <= 1:
        return RunMode.DEFAULT

    arg = sys.argv[1]

    if arg == RunMode.DEV.value:
        return RunMode.DEV
    elif arg == RunMode.PROD.value:
        return RunMode.PROD


def define_rms(rm: RunMode) -> bool:
    if rm not in [RunMode.PROD, RunMode.DEV]:
        return False

    glob.rms = _get_run_mode_settings(rm)
    return True


async def create_databases():
    os.makedirs(os.path.dirname(glob.rms.db_file_path), exist_ok=True)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        for query in await _get_create_table_scripts():
            await db.execute(query)
            await db.commit()


async def _get_create_table_scripts() -> list[str]:
    return [
        scripts.CREATE_TABLE_MEMBERS,
        scripts.CREATE_TABLE_ARTIFACTS,
        scripts.CREATE_TABLE_ADDT,
        scripts.CREATE_TABLE_DELT,
        scripts.CREATE_TABLE_TPAY,
        scripts.CREATE_TABLE_AWARDS,
        scripts.CREATE_TABLE_AWARD_MEMBER,
        scripts.CREATE_TABLE_PRICE_HISTORY,
        scripts.CREATE_TABLE_SALARY_PAYOUTS,
        scripts.CREATE_TABLE_PAID_MEMBERS,
        scripts.CREATE_TABLE_PAID_MEMBER_HISTORY
    ]


def _parse_pathlib(xml_path: str) -> str:
    path_split = xml_path.split('/')
    back_seq_count = 0

    for p in path_split:
        if p == '..':
            back_seq_count += 1
        else:
            break

    if back_seq_count == 0:
        path = Path.cwd()
    else:
        path = Path.cwd().parent
        for i in range(1, back_seq_count):
            path = path.parent

    for i in range(back_seq_count, len(path_split)):
        path /= path_split[i] if (i == len(path_split) - 1) else Path(path_split[i])

    p = str(path)
    return p


def _get_run_mode_settings(run_mode: RunMode) -> RunModeSettings:
    config_path_dev = _parse_pathlib(glob.CONFIG_PATH_DEV)
    config_path_prod = _parse_pathlib(glob.CONFIG_PATH_PROD)

    paths = [config_path_dev, config_path_prod]

    for fp in paths:
        if not os.path.exists(fp):
            continue

        root = ET.parse(fp).getroot()

        for settings in root.findall(".//settings"):
            if settings.attrib.get("mode") == run_mode.value:
                return RunModeSettings(
                    bot_token=settings.find("bot-token").text,
                    group_chat_id=int(settings.find("group-chat-id").text),
                    db_backup_chat_id=int(settings.find("db-backup-chat-id").text),
                    db_file_path=_parse_pathlib(settings.find("db-file-path").text)
                )

        raise ValueError(f"No settings found with name '{run_mode.value}'")

    raise IOError("All provided paths do not exist!")
