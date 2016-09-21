import json


class SortedListEncoder(json.JSONEncoder):

    def encode(self, obj):
        def sort_lists(item):
            if isinstance(item, list):
                return sorted(sort_lists(i) for i in item)
            elif isinstance(item, dict):
                return {k: sort_lists(v) for k, v in item.items()}
            else:
                return item

        return super(SortedListEncoder, self).encode(sort_lists(obj))
