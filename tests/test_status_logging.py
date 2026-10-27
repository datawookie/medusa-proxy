from proxy.tor import STATUS_HEADER, format_status


def test_status_rows_align_with_header_and_use_country_codes():
    rows = [
        format_status(
            10000,
            "185.220.101.31",
            12773,
            {
                "countryCode": "DE",
                "city": "Brandenburg an der Havel",
                "lat": 52.62,
                "lon": 13.12,
            },
        ),
        format_status(
            10001,
            "45.66.35.35",
            7706,
            {"countryCode": "NL", "city": "Amsterdam", "lat": 52.36, "lon": 4.79},
        ),
        format_status(10002, "---", "----"),
    ]

    separators = [
        tuple(index for index, char in enumerate(line) if char == "|")
        for line in [STATUS_HEADER, *rows]
    ]
    assert len(set(separators)) == 1
    assert "(DE) Brandenburg an der Havel" in rows[0]
    assert "(NL) Amsterdam" in rows[1]
    assert "Germany" not in rows[0]
    assert "---" in rows[2].split("|")[-1]
