from cmake_ls.signatures import SignatureParser, SignatureMatcher


def test():
    sig_str = "<target> [SYSTEM] [AFTER|BEFORE] <INTERFACE|PUBLIC|PRIVATE> <items> ..."
    parser = SignatureParser(sig_str)
    elements = parser.parse()
    print("Parsed Elements:", elements)

    matcher = SignatureMatcher(elements)

    # Valid
    res = matcher.match(["mytarget", "SYSTEM", "PUBLIC", "src/include"])
    print(f"Match 1 (Valid): {res.success} {res.message}")

    # Valid - repeated items
    res = matcher.match(["mytarget", "PUBLIC", "inc1", "inc2", "inc3"])
    print(f"Match 2 (Valid Repeated): {res.success} {res.message}")

    # Invalid - missing required choice
    res = matcher.match(["mytarget", "SYSTEM"])
    print(f"Match 3 (Invalid): {res.success} {res.message}")

    # Invalid - wrong choice
    res = matcher.match(["mytarget", "INVALID", "PUBLIC", "inc"])
    print(f"Match 4 (Invalid Choice): {res.success} {res.message}")

    # message specialization
    msg_sig = "STATUS <message>"
    parser_msg = SignatureParser(msg_sig)
    elements_msg = parser_msg.parse()
    matcher_msg = SignatureMatcher(elements_msg)

    res = matcher_msg.match(["STATUS", "hello world"])
    print(f"Match Msg (Valid): {res.success} {res.message}")

    res = matcher_msg.match(["hello world"])
    print(f"Match Msg (Invalid): {res.success} {res.message}")


if __name__ == "__main__":
    test()
