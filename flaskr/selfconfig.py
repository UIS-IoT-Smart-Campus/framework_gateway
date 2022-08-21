import configparser

FILE = 'init.cfg'

def get_config_values() -> dict:
    settings = {}
    config = configparser.ConfigParser()
    config.readfp(open(FILE))
    settings['standalone'] = config.getboolean('DEFAULT','standalone')
    #StandAlone Config
    settings['devicebrokerurl'] = config.get('standalone.config','devicebrokerurl')
    settings['devicebrokerport'] = config.getint('standalone.config','devicebrokerport')
    settings['devicebrokertopic'] = config.get('standalone.config','devicebrokertopic')
    settings['mqttclient'] = config.get('standalone.config','mqttclient')
    settings['mqttkeepalive'] = config.getint('standalone.config','mqttkeepalive')
    #NoStandAlone Config
    settings["backendurl"] = config.get('nostandalone.config','backendurl')
    settings["backendport"] = config.getint('nostandalone.config','backendport')
    settings["brokerbackendurl"] = config.get('nostandalone.config','brokerbackendurl')
    settings["brokerbackendport"] = config.get('nostandalone.config','brokerbackendport')
    settings["brokerbackendtopic"] = config.get('nostandalone.config','brokerbackendtopic')
    settings["global_id"] = config.getint('nostandalone.config','global_id')
    settings["gateway_ipv4"] = config.get('nostandalone.config','gateway_ipv4')

    return settings


def set_config_values(settings):
    last_settings = get_config_values()
    default_settings = {}
    standalone_settings = {}
    nostandalone_settings = {}

    standalone_settings_properties = [
        'devicebrokerurl',
        'devicebrokerport',
        'devicebrokertopic',
        'mqttclient',
        'mqttkeepalive'
    ]

    nostandalone_settings_properties = [
        'backendurl',
        'backendport',
        'brokerbackendurl',
        'brokerbackendport',
        'brokerbackendtopic',
        'global_id',
        'gateway_ipv4'
    ]

    if 'standalone' in settings:
        default_settings['standalone'] = settings['standalone']
    else:
        default_settings['standalone'] = last_settings['standalone']
    last_settings.pop('standalone')

    for key in standalone_settings_properties:
        if key in settings:
            standalone_settings[key] = settings[key]
        else:
            standalone_settings[key] = last_settings[key]
    
    for key in nostandalone_settings_properties:
        if key in settings:
            nostandalone_settings[key] = settings[key]
        else:
            nostandalone_settings[key] = last_settings[key]    
    
    #Save Settings
    config = configparser.ConfigParser()
    config['DEFAULT'] = default_settings
    config['standalone.config'] = standalone_settings
    config['nostandalone.config'] = nostandalone_settings
    with open('init.cfg', 'w') as configfile:
        config.write(configfile)
    return last_settings