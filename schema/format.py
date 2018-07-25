
import re
import jsonschema
from jsonschema import compat


# NOTE: All of the below regular expressions are terminated with
#       "\Z", rather than simply "$" to ensure a string with a
#       trailing newline is NOT matched.

# difference between hostname and domain name is hostname accepts wildcard
# at the beginning character for wildcard DNS record. But domain name doesn't
# allow wildcard.
RE_HOSTNAME = r'^(?!.{255,})(?:(?:^\*|(?!\-)[A-Za-z0-9_\-]{1,63})(?<!\-)\.)+\Z'
RE_DOMAINNAME = r'^(?!.{255,})(?:(?!\-)[A-Za-z0-9_\-]{1,63}(?<!\-)\.)+\Z'

RE_SRV_HOST_NAME = r'^(?:(?!\-)(?:\_[A-Za-z0-9_\-]{1,63}\.){2})(?!.{255,})' \
                   r'(?:(?!\-)[A-Za-z0-9_\-]{1,63}(?<!\-)\.)+\Z'

RE_UUID = r'^(?:[0-9a-fA-F]){8}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-' \
          r'(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){12}\Z'

RE_IP_AND_PORT = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}' \
                 r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' \
                 r'(?::(?:6553[0-5]|655[0-2]\d|65[0-4]\d\d|6[0-4]\d{3}' \
                 r'|[1-5]\d{4}|[1-9]\d{0,3}|0))?\Z'

RE_URL = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

RE_IP_OR_CIDR = r'^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.' \
                 '(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.' \
                 '(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.' \
                 '(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)($|/(\d|[1-2]\d|3[0-2]))?$'

RE_CIDR = r'^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.' \
           '(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.' \
           '(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.' \
           '(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)/(\d|[1-2]\d|3[0-2])\Z'

draft4_format_checker = jsonschema.draft4_format_checker

@draft4_format_checker.checks("url")
def is_url(instance):
    if not isinstance(instance, compat.str_types):
        return True

    # allow url omitting scheme
    if (not instance.startswith('http://') and
        not instance.startswith('https://')):
        instance = 'http://' + instance

    if not re.match(RE_URL, instance):
        return False

    return True



@draft4_format_checker.checks("hostname")
def is_hostname(instance):
    if not isinstance(instance, compat.str_types):
        return True

    # FQDN expects the dot at the end of the name
    if not instance.endswith('.'):
        instance = instance + "."

    if not re.match(RE_HOSTNAME, instance):
        return False

    return True

@draft4_format_checker.checks("domainname")
def is_domainname(instance):
    if not isinstance(instance, compat.str_types):
        return True

    # FQDN expects the dot at the end of the name
    if not instance.endswith('.'):
        instance = instance + "."

    if not re.match(RE_DOMAINNAME, instance):
        return False

    return True

@draft4_format_checker.checks("srv-hostname")
def is_srv_hostname(instance):
    if not isinstance(instance, compat.str_types):
        return True

    if not instance.endswith('.'):
        instance = instance + "."

    if not re.match(RE_SRV_HOST_NAME, instance):
        return False

    return True

@draft4_format_checker.checks("ip-or-host")
def is_ip_or_host(instance):
    if not isinstance(instance, compat.str_types):
        return True

    if not instance.endswith('.'):
        instance = instance + "."

    comps = str(instance).split('.')
    if len(comps)>0 and all(map(str.isdigit, comps)):
        if not is_ipv4(instance):
            return False
        else:
            return True

    if not re.match(RE_HOSTNAME, instance):
        return False

    return True


@draft4_format_checker.checks("email")
def is_email(instance):
    if not isinstance(instance, compat.str_types):
        return True

    if instance.count('@') != 1 or instance.endswith('@'):
        return False

    rname = instance.replace('@', '.', 1)

    if not re.match(RE_DOMAINNAME, "%s." % rname):
        return False

    return True


@draft4_format_checker.checks("uuid")
def is_uuid(instance):
    if not isinstance(instance, compat.str_types):
        return True

    if not re.match(RE_UUID, instance):
        return False

    return True


@draft4_format_checker.checks("ip-and-port")
def is_ip_and_port(instance):
    if not isinstance(instance, compat.str_types):
        return True

    if not re.match(RE_IP_AND_PORT, instance):
        return False

    return True


@draft4_format_checker.checks("ip-or-cidr")
def is_ip_or_cidr(instance):
    if not isinstance(instance, compat.str_types):
        return True

    if not re.match(RE_IP_OR_CIDR, instance):
        return False

    return True


@draft4_format_checker.checks("cidr")
def is_cidr(instance):
    if not isinstance(instance, compat.str_types):
        return True

    if not re.match(RE_CIDR, instance):
        return False

    return True
