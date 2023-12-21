# from jsonschema import ErrorTree


def set_message(tree: dict, path: list, message: str):
    field = path.pop(0)
    if field not in tree:
        tree[field] = {} if path else []
    if not path:
        tree[field].append(message)
    else:
        set_message(tree[field], path, message)
    
def get_validator_error_tree(validator, data):
# validator = jsonschema.Draft7Validator(schema)
    errors = validator.iter_errors(data)
    # return ErrorTree(errors)
    tree = {}
    for error in errors:
        try:
            set_message(tree, list(error.path), error.message)
        except:
            pass# raise Exception('path error', error.path, error.message)
    return tree
        # print(list(error.path))
        # print(error.message)
        # print('---------')