import json

from kano.utils.shell import run_cmd
from kano.utils.hardware import get_rpi_model, get_board_property
from kano.logging import logger

from kano_settings.system.display import get_status, get_model, set_hdmi_mode, \
    get_edid, set_full_range, write_overscan_values, set_overscan_state
from kano_settings.system.audio import is_HDMI, set_to_HDMI
from kano_settings.boot_config import \
    get_config_comment, get_config_value, has_config_comment


def is_model_configured(model):
    return get_config_comment('kano_screen_used', model)


def fix_hdmi_audio(edid):
    if not edid['hdmi_audio'] and is_HDMI():
        msg = 'hdmi audio not supported on this screen, changing to analogue'
        logger.info(msg)
        set_to_HDMI(False)


def is_screen_explicitly_configured(model):
    if get_config_value('hdmi_group') != 0 and \
            get_config_value('hdmi_mode') != 0:
        if not has_config_comment('kano_screen_used') or \
                get_config_comment('kano_screen_used', model):
            # The screen is either the same or not set at all
            logger.info('Explicit HDMI configuration detected, exiting.')
            return True
        else:
            # New screen detected, will reconfigure
            logger.info('New screen was detected.')

    return False


def parse_screen_data(screen_data):
    status = screen_data.get('status')
    edid = screen_data.get('edid')

    return edid, status


def override_models(overrides, edid, model):
    for override_model, override_rules in overrides.iteritems():
        if override_model == model:
            edid['target_group'] = override_rules['target_group']
            edid['target_mode'] = override_rules['target_mode']
            edid['is_monitor'] = override_rules['is_monitor']
            return


def calculate_is_monitor(edid):
    edid['target_full_range'] = edid['is_monitor']


def compare_and_set_mode(edid, status):
    if status['group'] == edid['target_group'] and \
       status['mode'] == edid['target_mode']:
        logger.info('mode change not needed')
        return False

    logger.info('mode change needed')
    modes = '{} {}'.format(edid['target_group'], edid['target_mode'])
    logger.info('setting mode: {}'.format(modes))

    set_hdmi_mode(edid['target_group'], edid['target_mode'])
    return True


def compare_and_set_full_range(edid, status):
    if status['full_range'] == edid['target_full_range']:
        logger.info('fullrange change not needed')
        return False

    logger.info('fullrange change needed')
    msg = 'setting fullrange to: {}'.format(edid['target_full_range'])
    logger.info(msg)
    set_full_range(edid['target_full_range'])

    return True


def compare_and_set_overscan(edid, status):
    if status['overscan'] == edid['target_overscan']:
        logger.info('overscan change not needed')
        return False

    logger.info('overscan change needed')
    logger.info('setting overscan to: {}'.format(edid['target_overscan']))

    if edid['target_overscan']:
        set_overscan_state(True)
        overscan_value = -48
    else:
        set_overscan_state(False)
        overscan_value = 0

    write_overscan_values(
        {
            'top': overscan_value,
            'bottom': overscan_value,
            'left': overscan_value,
            'right': overscan_value,
        },
        end_transaction=False
    )

    return True


def get_screen_information(screen_log_path):
    """ Retrieves the information about the current screen.

        The data will be logged to the bootpartition for
        troubleshooting purposes.
    """

    info = {
        "edid": get_edid(),
        "model": get_model(),
        "status": get_status()
    }

    with open(screen_log_path, 'w') as f:
        json.dump(info, f, sort_keys=True, indent=4, separators=(',', ': '))

    return info


def ensure_correct_browser(dry_run=False):
    model = get_rpi_model()
    arch = get_board_property(model, 'arch')
    chromium_support = arch not in ['armv6']

    if chromium_support:
        browser = 'chromium-browser'
    else:
        browser = 'epiphany-browser'

    if dry_run:
        logger.debug("browser should be {}".format(browser))
    else:
        run_cmd('update-alternatives --set x-www-browser /usr/bin/{}'
                .format(browser))
