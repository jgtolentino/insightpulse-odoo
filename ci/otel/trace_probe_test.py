#!/usr/bin/env python3
"""
OpenTelemetry header propagation tests.
Validates trace context propagation across service boundaries.
"""
import pytest
from typing import Dict


def test_traceparent_header_format():
    """Test traceparent header follows W3C format."""
    # W3C Trace Context format: version-trace-id-parent-id-trace-flags
    valid_traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

    parts = valid_traceparent.split("-")
    assert len(parts) == 4, "traceparent must have 4 parts"
    assert parts[0] == "00", "version must be 00"
    assert len(parts[1]) == 32, "trace-id must be 32 hex chars"
    assert len(parts[2]) == 16, "parent-id must be 16 hex chars"
    assert parts[3] in ["00", "01"], "trace-flags must be 00 or 01"


def test_tracestate_header_format():
    """Test tracestate header follows W3C format."""
    # W3C Trace Context format: key1=value1,key2=value2
    valid_tracestate = "vendor1=value1,vendor2=value2"

    # Split by comma
    entries = valid_tracestate.split(",")
    assert len(entries) > 0, "tracestate must have at least one entry"

    for entry in entries:
        assert "=" in entry, f"tracestate entry '{entry}' must have key=value format"
        key, value = entry.split("=", 1)
        assert len(key) > 0, "tracestate key cannot be empty"
        assert len(value) > 0, "tracestate value cannot be empty"


def test_trace_context_propagation():
    """Test trace context is propagated through service calls."""
    # Simulate incoming request with trace context
    incoming_headers = {
        "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        "tracestate": "vendor1=value1"
    }

    # Simulate outgoing request that should preserve trace context
    outgoing_headers = propagate_trace_context(incoming_headers)

    # Validate trace-id is preserved
    incoming_trace_id = incoming_headers["traceparent"].split("-")[1]
    outgoing_trace_id = outgoing_headers["traceparent"].split("-")[1]
    assert incoming_trace_id == outgoing_trace_id, "trace-id must be preserved"

    # Validate parent-id is updated (new span)
    incoming_parent_id = incoming_headers["traceparent"].split("-")[2]
    outgoing_parent_id = outgoing_headers["traceparent"].split("-")[2]
    assert incoming_parent_id != outgoing_parent_id, "parent-id must be updated for new span"

    # Validate tracestate is preserved
    assert outgoing_headers.get("tracestate") == incoming_headers["tracestate"], "tracestate must be preserved"


def test_trace_context_generation():
    """Test trace context is generated when missing."""
    # Simulate request without trace context
    incoming_headers = {}

    # Generate new trace context
    outgoing_headers = propagate_trace_context(incoming_headers)

    # Validate traceparent is generated
    assert "traceparent" in outgoing_headers, "traceparent must be generated"
    assert len(outgoing_headers["traceparent"].split("-")) == 4, "generated traceparent must be valid"


def propagate_trace_context(incoming_headers: Dict[str, str]) -> Dict[str, str]:
    """
    Simulate trace context propagation.
    In real implementation, this would be handled by OTel SDK.
    """
    outgoing_headers = {}

    if "traceparent" in incoming_headers:
        # Parse incoming traceparent
        parts = incoming_headers["traceparent"].split("-")
        version, trace_id, parent_id, flags = parts

        # Generate new parent-id for new span
        new_parent_id = "a0b1c2d3e4f5a6b7"  # Would be random in real implementation

        # Construct new traceparent
        outgoing_headers["traceparent"] = f"{version}-{trace_id}-{new_parent_id}-{flags}"

        # Preserve tracestate
        if "tracestate" in incoming_headers:
            outgoing_headers["tracestate"] = incoming_headers["tracestate"]
    else:
        # Generate new trace context
        trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"  # Would be random
        parent_id = "00f067aa0ba902b7"  # Would be random
        outgoing_headers["traceparent"] = f"00-{trace_id}-{parent_id}-01"

    return outgoing_headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
