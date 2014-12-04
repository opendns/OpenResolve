from dns import rdatatype, rdataclass, flags, rcode


def parse_query(query, nameserver, duration):
    """ Parse a dns response into a dict based on record type.
    Should adhere to propsed rfc format:
    http://tools.ietf.org/html/draft-bortzmeyer-dns-json-00
    """
    flag_list = flags.to_text(query.response.flags)
    return {
        'Query': get_query(nameserver, duration),
        'QuestionSection': get_question(query),
        'AnswerSection': get_rrs_from_rrsets(query.response.answer),
        'AdditionalSection': get_rrs_from_rrsets(query.response.additional),
        'AuthoritySection': get_rrs_from_rrsets(query.response.authority),
        'ReturnCode': rcode.to_text(query.response.rcode()),
        'ID': query.response.id,
        'AA': 'AA' in flag_list,
        'TC': 'TC' in flag_list,
        'RD': 'RD' in flag_list,
        'RA': 'RA' in flag_list,
        'AD': 'AD' in flag_list
    }


def get_query(nameserver, duration):
    return {
        "Server": nameserver,
        "Duration": duration  # this is a float, which deviates from the RFC
    }


def get_question(query):
    return {
        "Qname": str(query.qname),
        "Qtype": rdatatype.to_text(query.rdtype),
        "Qclass": rdataclass.to_text(query.rdclass)
    }


def get_rrs_from_rrsets(rrsets):
    """This works for answer, authority, and additional rrsets"""
    rr_list = []
    for rrset in rrsets:
        common_rr_dict = {
            "Name":  str(rrset.name),
            "Type": rdatatype.to_text(rrset.rdtype),
            "Class": rdataclass.to_text(rrset.rdclass),
            "TTL": rrset.ttl  # TODO: doesn't each rr have it's own ttl?
        }
        for rr in rrset:
            rr_dict = common_rr_dict.copy()
            rr_dict.update(get_record_specific_answer_fields(rr))
            rr_list.append(rr_dict)
    return rr_list


def get_record_specific_answer_fields(rr):
    """ Return a json object of fields specific to a given record type for a
    given dns answer.
    E.g. 'A' records have an 'address' field. 'NS' hava a 'target' field etc.
    """
    if rr.rdtype == rdatatype.A or rr.rdtype == rdatatype.AAAA:
        return {"Address": rr.address}

    if (rr.rdtype == rdatatype.CNAME or
            rr.rdtype == rdatatype.PTR or
            rr.rdtype == rdatatype.NS):
        return {"Target": str(rr.target)}

    if rr.rdtype == rdatatype.MX:
        return {
            "Preference": rr.preference,
            "MailExchanger": str(rr.exchange)
        }

    if rr.rdtype == rdatatype.SOA:
        return {
            "MasterServerName": str(rr.mname),
            "MaintainerName": str(rr.rname),
            "Serial": rr.serial,
            "Refresh": rr.refresh,
            "Retry": rr.retry,
            "Expire": rr.expire,
            "NegativeTtl": rr.minimum  # Note: keyname changes in JSON RFC
        }

    if rr.rdtype == rdatatype.TXT:
        # TXT was not described in the JSON RFC
        return {
            "TxtData": str(rr),
        }

    if rr.rdtype == rdatatype.NAPTR:
        return {
            "Flags": rr.flags,
            "Order": rr.order,
            "Service": rr.service,
            "Preference": rr.preference,
            "Regexp": rr.regexp,
            "Replacement": str(rr.replacement)
        }

    if rr.rdtype == rdatatype.LOC:
        return {
            "Altitude": rr.altitude / 100,  # .altitude is in centimeters
            "Longitude": rr.longitude,
            "Latitude": rr.latitude
        }

    return {}
