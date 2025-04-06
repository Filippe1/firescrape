import dns.resolver

def has_mx_record(domain):
    try:
        # Query MX records for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False

def is_valid_domain(email):
    domain = email.split('@')[-1]
    return has_mx_record(domain)

# Example usage
email = "test@example.com"
if is_valid_domain(email):
    print("Domain has valid MX records.")
else:
    print("Domain does not have valid MX records.")