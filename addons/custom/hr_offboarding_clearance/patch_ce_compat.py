#!/usr/bin/env python3
"""Patch hr_offboarding.py for CE compatibility by commenting out Enterprise features"""

import re

# Read the file
with open("models/hr_offboarding.py", "r") as f:
    content = f.read()

# Comment out sign_request_id field definition
content = re.sub(
    r"(    # Signature Management\n    sign_request_id = fields\.Many2one\(\n        \'sign\.request\',[\s\S]*?    \))",
    r"    # # Signature Management (requires Enterprise Sign module)\n    # \1",
    content,
    flags=re.MULTILINE,
)

# Comment out sign_status field
content = re.sub(
    r"(    sign_status = fields\.Selection\(\n        related=\'sign_request_id\.state\',[\s\S]*?    \))",
    r"    # \1",
    content,
    flags=re.MULTILINE,
)

# Comment out helpdesk_ticket_id field
content = re.sub(
    r"(    # Helpdesk Integration\n    helpdesk_ticket_id = fields\.Many2one\(\n        \'helpdesk\.ticket\',[\s\S]*?    \))",
    r"    # # Helpdesk Integration (requires Enterprise Helpdesk module)\n    # \1",
    content,
    flags=re.MULTILINE,
)

# Comment out _create_helpdesk_ticket method
content = re.sub(
    r"(    def _create_helpdesk_ticket\(self\):[\s\S]*?        self\.helpdesk_ticket_id = ticket\.id)",
    r"    # \1",
    content,
    flags=re.MULTILINE,
)

# Comment out sign request creation in _route_clearance_form
content = re.sub(
    r"(            sign_request = self\.env\[\'sign\.request\'\]\.create\(\{[\s\S]*?            record\.sign_request_id = sign_request\.id)",
    r"            # \1",
    content,
    flags=re.MULTILINE,
)

# Write the patched content
with open("models/hr_offboarding.py", "w") as f:
    f.write(content)

print("✅ Patched hr_offboarding.py for CE compatibility")
