from typing import List

from click import Context, Parameter, ParamType, echo
from click.shell_completion import CompletionItem

from quick_manage.environment import Environment


class HostNameType(ParamType):
    name = "host-name"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        return [CompletionItem(x) for x in env.host_configs.keys() if x.startswith(incomplete)]


class StoreVarType(ParamType):
    name = "key-store"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        return [CompletionItem(x) for x in env.key_stores.keys() if x.startswith(incomplete)]


class KeyNameType(ParamType):
    name = "key-name"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        store_name = ctx.params.get("store_name", None)
        try:
            flattened = []
            for _, result in env.list_keys(store_name).items():
                flattened += result['keys']
            return [CompletionItem(x) for x in flattened if x.startswith(incomplete)]
        except KeyError:
            return []
