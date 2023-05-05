import os


def type_to_kconfig_type(val):
    t = type(val)
    if (t is str):
        return "string"
    elif (t is int):
        return "int"
    elif (t is bool):
        return "bool"
    else:
        return "string"


def wrap(value):
    if type(value) is str:
        return '"{}"'.format(value)
    else:
        return str(value)


def convert_to_int_if_int(str_int):
    try:
        return int(str_int)
    except ValueError:
        return str_int


def convert_to_int_if_int(str_int):
    try:
        return int(str_int)
    except ValueError:
        return str_int


def main():
    kconfig_template = '''
menu "Environment Variables"

{}
endmenu
'''

    env_variable_template = '''
config {}
    {} "{}"
    default {}
    help
        Environment variable: {}
'''

    kconfig_content = []

    for key, value in os.environ.items():
        value = convert_to_int_if_int(value)
        print(key, value, type(value))
        if key.startswith("SESP_"):
            key = key[5:]
            kconfig_content.append(env_variable_template.format(
                key, type_to_kconfig_type(value), key, wrap(value), key))

    proj_build_file = "/workspace/main/Kconfig.projbuild"
    if os.path.exists(proj_build_file):
        os.remove(proj_build_file)
    with open(proj_build_file, "w") as f:
        f.write(kconfig_template.format("".join(kconfig_content)))


if __name__ == "__main__":
    main()
    print("Done transfering env vars to Kconfig.projbuild")


# import os


# def read_env():
#     env_vars = {}
#     for key, value in os.environ.items():
#         value = convert_to_int_if_int(value)
#         if key.startswith("SESP_"):
#             key = key[5:]
#             env_vars[key] = value

#     return env_vars

# def update_sdkconfig_defaults(env_vars, sdkconfig_defaults_path):
#     with open(sdkconfig_defaults_path, 'w') as f:
#         for key, value in env_vars.items():
#             f.write(f'CONFIG_{key}={wrap(value)}\n')
#         print(f"Updated {sdkconfig_defaults_path} with environment variables")

# if __name__ == '__main__':
#     sdkconfig_defaults_path = '/workspace/sdkconfig.defaults'
#     env_vars = read_env()
#     update_sdkconfig_defaults(env_vars, sdkconfig_defaults_path)
