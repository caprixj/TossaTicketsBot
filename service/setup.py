import os
import sys
import xml.etree.ElementTree as ET
from typing import Optional

import aiosqlite

from pathlib import Path

import resources.glob as glob
from model.types.run_mode import RunMode, RunModeSettings
from resources.funcs import get_materials_yaml
from repository import sql


def define_run_mode() -> Optional[RunMode]:
    if len(sys.argv) <= 1:
        return RunMode.DEFAULT

    arg = sys.argv[1]

    if arg == RunMode.DEV.value:
        return RunMode.DEV
    elif arg == RunMode.PROD.value:
        return RunMode.PROD
    return None


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
            sql.INSERT_OR_IGNORE_MATERIALS,
            [(m.name, m.emoji) for m in await get_materials_yaml()]
        )
        await db.commit()


async def _insert_sql_vars():
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.executemany(
            sql.INSERT_OR_IGNORE_SQL_VARS, [
                (glob.NBT_SQL_VAR, 0)
            ]
        )
        await db.commit()


async def _get_create_table_scripts() -> list[str]:
    return [
        sql.CREATE_VARS,
        sql.CREATE_MEMBERS,
        sql.CREATE_DEL_MEMBERS,
        sql.CREATE_ARTIFACTS,
        # sql.CREATE_ARTIFACT_VALUE_HISTORY,
        sql.CREATE_TICKET_TXNS,
        sql.CREATE_TAX_TXNS,
        sql.CREATE_BUSINESS_PROFITS,
        sql.CREATE_BUSINESS_WITHDRAWS,
        sql.CREATE_AWARDS,
        sql.CREATE_AWARD_MEMBER,
        sql.CREATE_RATE_HISTORY,
        sql.CREATE_SALARY_PAYOUTS,
        sql.CREATE_EMPLOYEES,
        sql.CREATE_EMPLOYMENT_HISTORY,
        sql.CREATE_JOBS,
        sql.CREATE_PRICES,
        sql.CREATE_PRICE_HISTORY,
        sql.CREATE_MATERIALS,
        sql.CREATE_MEMBER_MATERIALS,
        sql.CREATE_MAT_TXNS,
        sql.CREATE_MAT_TXN_INVOICES,
        sql.CREATE_DAILY_SCHEDULES,
        # sql.CREATE_ACTIVITY_DATA
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
    config_paths = [
        _parse_pathlib(glob.CONFIG_PATH_DEV),
        _parse_pathlib(glob.CONFIG_PATH_PROD),
    ]

    for fp in config_paths:
        if not os.path.exists(fp):
            continue

        root = ET.parse(fp).getroot()
        for settings in root.findall('.//settings'):
            if settings.get('mode') != run_mode.value:
                continue

            bot_token = settings.find('bot-token').text
            main_chat_id = int(settings.find('main-chat-id').text)
            backup_id = int(settings.find('db-backup-chat-id').text)
            db_path = _parse_pathlib(settings.find('db-file-path').text)

            chat_ids_block = settings.find('side-chat-ids')
            if chat_ids_block is not None:
                side_chat_ids = [
                    int(e.text) for e in chat_ids_block.findall('chat-id')
                    if e.text and e.text.strip()
                ]
            else:
                side_chat_ids = []

            return RunModeSettings(
                bot_token=bot_token,
                main_chat_id=main_chat_id,
                side_chat_ids=side_chat_ids,
                db_backup_chat_id=backup_id,
                db_file_path=db_path
            )

        raise ValueError(f"No settings found for mode '{run_mode.value}'")

    raise IOError('All provided config paths do not exist!')
