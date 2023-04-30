import os
import re

def main():
    kconfig_template = '''
menu "Environment Variables"

{}
endmenu
'''

    env_variable_template = '''
config {}
    string "{}"
    default "{}"
    help
        Environment variable: {}
'''

    kconfig_content = []

    for key, value in os.environ.items():
        if key.startswith("ESP_"):
            config_key = re.sub(r'\W', '_', key)
            kconfig_content.append(env_variable_template.format(config_key, key, value, key))


    with open("/workspace/main/Kconfig.projbuild/", "w") as f:
        f.write(kconfig_template.format("".join(kconfig_content)))

if __name__ == "__main__":
    main()
    print("Done!")
