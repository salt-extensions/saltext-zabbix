"""
Return salt data to Zabbix

The following Type: "Zabbix trapper" with "Type of information" Text items are required:

.. code-block:: cfg

    Key: salt.trap.info
    Key: salt.trap.warning
    Key: salt.trap.high

To use the Zabbix returner, append '--return zabbix' to the salt command. ex:

.. code-block:: bash

    salt '*' test.ping --return zabbix
"""

import os

# Define the module's virtual name
__virtualname__ = "zabbix"


def __virtual__():
    if zbx():
        return True
    return False, "Zabbix returner: No zabbix_sender and zabbix_agend.conf found."


def zbx():
    if os.path.exists("/usr/local/zabbix/bin/zabbix_sender") and os.path.exists(
        "/usr/local/zabbix/etc/zabbix_agentd.conf"
    ):
        zabbix_sender = "/usr/local/zabbix/bin/zabbix_sender"
        zabbix_config = "/usr/local/zabbix/etc/zabbix_agentd.conf"
        return {"sender": zabbix_sender, "config": zabbix_config}
    elif os.path.exists("/usr/bin/zabbix_sender") and os.path.exists(
        "/etc/zabbix/zabbix_agentd.conf"
    ):
        zabbix_sender = "/usr/bin/zabbix_sender"
        zabbix_config = "/etc/zabbix/zabbix_agentd.conf"
        return {"sender": zabbix_sender, "config": zabbix_config}
    else:
        return False


def zabbix_send(key, output):
    cmd = zbx()["sender"] + " -c " + zbx()["config"] + " -k " + key + ' -o "' + output + '"'
    __salt__["cmd.shell"](cmd)


def save_load(jid, load, minions=None):  # pylint: disable=unused-argument
    """
    Included for API consistency
    """


def returner(ret):
    changes = False
    errors = False
    job_minion_id = ret["id"]

    if isinstance(ret["return"], dict):
        for item in ret["return"].values():
            if "comment" in item and "name" in item and item["result"] is False:
                errors = True
                zabbix_send(
                    "salt.trap.high",
                    f"SALT:\nname: {item['name']}\ncomment: {item['comment']}",
                )
            elif "comment" in item and "name" in item and item["changes"]:
                changes = True
                zabbix_send(
                    "salt.trap.warning",
                    f"SALT:\nname: {item['name']}\ncomment: {item['comment']}",
                )

    if not changes and not errors:
        zabbix_send("salt.trap.info", f"SALT {job_minion_id} OK")
