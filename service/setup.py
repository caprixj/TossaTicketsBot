import os
import sys
import xml.etree.ElementTree as ET

import aiosqlite

from pathlib import Path

import resources.const.glob as glob
from model.types.run_mode import RunMode, RunModeSettings
from resources.funcs.funcs import get_materials_yaml
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
    await _create_tables()
    await _insert_materials()
    await _insert_sql_vars()


async def _create_tables():
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        for query in await _get_create_table_scripts():
            await db.execute(query)
            await db.commit()


async def _insert_materials():
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.executemany(
            scripts.INSERT_OR_IGNORE_MATERIALS,
            [(m.name, m.emoji) for m in await get_materials_yaml()]
        )
        await db.commit()


async def _insert_sql_vars():
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.executemany(
            scripts.INSERT_OR_IGNORE_SQL_VARS,
            [
                (glob.NBT_SQL_VAR, '0.00')
            ]
        )
        await db.commit()


async def _get_create_table_scripts() -> list[str]:
    return [
        scripts.CREATE_VARS,
        scripts.CREATE_MEMBERS,
        scripts.CREATE_ARTIFACTS,
        scripts.CREATE_ARTIFACT_VALUE_HISTORY,
        scripts.CREATE_ADDT,
        scripts.CREATE_DELT,
        scripts.CREATE_TPAY,
        scripts.CREATE_BUSINESS_PROFITS,
        scripts.CREATE_BUSINESS_WITHDRAWS,
        scripts.CREATE_AWARDS,
        scripts.CREATE_AWARD_MEMBER,
        scripts.CREATE_RATE_HISTORY,
        scripts.CREATE_SALARY_PAYOUTS,
        scripts.CREATE_EMPLOYEES,
        scripts.CREATE_EMPLOYMENT_HISTORY,
        scripts.CREATE_JOBS,
        scripts.CREATE_PRICES,
        scripts.CREATE_PRICE_HISTORY,
        scripts.CREATE_MATERIALS,
        scripts.CREATE_MEMBER_MATERIALS,
        scripts.CREATE_MATERIAL_TRANSACTIONS,
        scripts.CREATE_MATERIAL_TRANSACTION_REQUESTS,
        scripts.CREATE_DAILY_SCHEDULES,
        scripts.CREATE_ACTIVITY_DATA
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

    return str(path)


def _get_run_mode_settings(run_mode: RunMode) -> RunModeSettings:
    config_path_dev = _parse_pathlib(glob.CONFIG_PATH_DEV)
    config_path_prod = _parse_pathlib(glob.CONFIG_PATH_PROD)

    paths = [config_path_dev, config_path_prod]

    for fp in paths:
        if not os.path.exists(fp):
            continue

        root = ET.parse(fp).getroot()

        for settings in root.findall('.//settings'):
            if settings.attrib.get('mode') == run_mode.value:
                return RunModeSettings(
                    bot_token=settings.find('bot-token').text,
                    main_chat_id=int(settings.find('main-chat-id').text),
                    db_backup_chat_id=int(settings.find('db-backup-chat-id').text),
                    db_file_path=_parse_pathlib(settings.find('db-file-path').text)
                )

        raise ValueError(f"No settings found with name '{run_mode.value}'")

    raise IOError('All provided paths do not exist!')
