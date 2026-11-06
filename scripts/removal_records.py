"""Exact, reviewable delistings; these records do not declare a site safe."""
import re
from datetime import datetime

HOST = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}\Z")


def removal_hosts(data):
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('domains'), dict):
        raise ValueError('invalid removal registry')
    result = set()
    for host, record in data['domains'].items():
        if not isinstance(host, str) or not HOST.fullmatch(host) or len(host) > 253:
            raise ValueError('removal scope must be an exact canonical hostname')
        if not isinstance(record, dict) or not record.get('reference') or not record.get('reason'):
            raise ValueError(f'missing removal provenance: {host}')
        when = datetime.fromisoformat(record.get('removed_at', '').replace('Z', '+00:00'))
        if when.tzinfo is None:
            raise ValueError(f'removal timestamp must include timezone: {host}')
        result.add(host)
    return result
