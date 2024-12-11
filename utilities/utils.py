import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

from model.functional.RunMode import RunMode
from model.functional.RunModeSettings import RunModeSettings
from utilities.global_vars import GlobalVariables as gv
from utilities.hidden_globals import permission_denied_messages


async def _parse_pathlib(xml_path: str) -> str:
    path_split = xml_path.split('/')
    back_seq_count = 0

    for p in path_split:
        if p == '..':
            back_seq_count += 1
        else:
            break

    path = None
    if back_seq_count == 0:
        path = Path()
    else:
        path = Path.cwd().parent
        for i in range(1, back_seq_count):
            path = path.parent

    for i in range(back_seq_count, len(path_split)):
        path /= path_split[i] if (i == len(path_split) - 1) else Path(path_split[i])

    return str(path)


async def get_run_mode_settings(run_mode: RunMode) -> RunModeSettings:
    config_path_dev = await _parse_pathlib(gv.CONFIG_PATH_DEV)
    config_path_prod = await _parse_pathlib(gv.CONFIG_PATH_PROD)

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


async def get_command_args(message_text: str) -> list[str]:
    if not message_text:
        return list()

    split = message_text.split(" ")
    split_stripped = []

    for i in split:
        if i != "":
            split_stripped.append(i)

    split_stripped.remove(split_stripped[0])

    return split_stripped
