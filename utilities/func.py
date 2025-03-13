import random
import os
import xml.etree.ElementTree as ET
from datetime import datetime

import utilities.globals as glob
from pathlib import Path

from model.database.Member import Member
from utilities.rand_globals import permission_denied_messages
from utilities.run_mode import RunMode, RunModeSettings
from utilities.sql_scripts import CREATE_TABLE_MEMBERS, CREATE_TABLE_ADDT, CREATE_TABLE_DELT, CREATE_TABLE_ARTIFACTS, \
    CREATE_TABLE_TPAY


async def _parse_pathlib(xml_path: str) -> str:
    path_split = xml_path.split('/')
    back_seq_count = 0

    for p in path_split:
        if p == '..':
            back_seq_count += 1
        else:
            break

    if back_seq_count == 0:
        path = Path().cwd()
    else:
        path = Path.cwd().parent
        for i in range(1, back_seq_count):
            path = path.parent

    for i in range(back_seq_count, len(path_split)):
        path /= path_split[i] if (i == len(path_split) - 1) else Path(path_split[i])

    return str(path)


async def get_run_mode_settings(run_mode: RunMode) -> RunModeSettings:
    config_path_dev = await _parse_pathlib(glob.CONFIG_PATH_DEV)
    config_path_prod = await _parse_pathlib(glob.CONFIG_PATH_PROD)

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
                    db_file_path=await _parse_pathlib(settings.find("db-file-path").text)
                )

        raise ValueError(f"No settings found with name '{run_mode.value}'")

    raise IOError("All provided paths do not exist!")


async def get_random_permission_denied_message() -> str:
    return permission_denied_messages[random.randint(0, len(permission_denied_messages) - 1)]


async def get_db_setup_sql_script() -> list[str]:
    return [
        CREATE_TABLE_MEMBERS,
        CREATE_TABLE_ARTIFACTS,
        CREATE_TABLE_ADDT,
        CREATE_TABLE_DELT,
        CREATE_TABLE_TPAY
    ]


async def get_transaction_time() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


async def get_fee(transfer_amount: int) -> int:
    if transfer_amount <= 10:
        return 1
    if transfer_amount <= 50:
        return round(0.2 * transfer_amount) + 1
    if transfer_amount <= 100:
        return round(0.4 * transfer_amount) + 1

    return round(0.6 * transfer_amount) + 1


async def get_formatted_name_by_member(member: Member, ping: bool = False) -> str:
    return await get_formatted_name(
        username=member.username,
        first_name=member.first_name,
        last_name=member.last_name,
        user_id=member.user_id,
        ping=ping
    )


async def get_formatted_name(
        username: str,
        first_name: str,
        last_name: str,
        user_id: int = 0,
        ping: bool = False) -> str:

    name = str()

    if first_name or last_name:
        fn_not_empty = False
        if first_name:
            fn_not_empty = True
            name += first_name
        if last_name:
            name += ' ' if fn_not_empty else ''
            name += last_name
    elif username:
        name += username
    else:
        name = glob.NO_NAMES_TEXT

    return name if not ping else \
        f'@{name}' if name == username else f'[{name}](tg://user?id={user_id})'
