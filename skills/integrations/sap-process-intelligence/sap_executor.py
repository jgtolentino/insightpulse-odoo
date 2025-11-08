#!/usr/bin/env python3
"""
SAP Process Intelligence - Executor
Main execution engine for SAP process mining skills.

Implements neurosymbolic reasoning over SAP event traces with
quantized local ML models for SOC2-compliant process intelligence.
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
import statistics

from models.sap_event_model import (
    EventTrace,
    ProcessVariant,
    ProcessDeviation,
    VariantSummary,
    Bottleneck,
    ResourceUtilization,
    KPIForecast,
    ProcessMapStatistics,
    ExtractEventsRequest,
    ExtractEventsResponse,
    CorrelateVariantsRequest,
    CorrelateVariantsResponse,
    PredictKPIRequest,
    PredictKPIResponse,
    AnalyzeBottlenecksRequest,
    AnalyzeBottlenecksResponse,
    GenerateProcessMapRequest,
    GenerateProcessMapResponse,
    ProcessType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SAPProcessIntelligence:
    """Main orchestrator for SAP Process Intelligence operations"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize SAP Process Intelligence engine.

        Args:
            config: Configuration dictionary with SAP connection details
        """
        self.config = config or {}
        self.sap_client = None  # Placeholder for SAP connection client
        logger.info("SAP Process Intelligence initialized")

    def extract_process_events(
        self, request: ExtractEventsRequest
    ) -> ExtractEventsResponse:
        """
        Extract process events from SAP via OData/BAPI.

        Args:
            request: Event extraction request

        Returns:
            ExtractEventsResponse with event traces
        """
        logger.info(f"Extracting events for process: {request.process_id}")

        # TODO: Implement actual SAP OData/BAPI extraction
        # This is a placeholder that would connect to SAP via:
        # - SAP OData services
        # - RFC/BAPI calls
        # - SAP Gateway APIs

        # For now, return mock data structure
        events = []
        extraction_timestamp = datetime.utcnow()

        return ExtractEventsResponse(
            events=events,
            total_events=len(events),
            extraction_timestamp=extraction_timestamp,
            system_id=request.system_id,
        )

    def correlate_variants(
        self, request: CorrelateVariantsRequest
    ) -> CorrelateVariantsResponse:
        """
        Identify process variants and deviations.

        Args:
            request: Variant correlation request

        Returns:
            CorrelateVariantsResponse with variant analysis
        """
        logger.info(f"Correlating variants from {len(request.events)} events")

        if not request.events:
            return CorrelateVariantsResponse(
                variant_summary=VariantSummary(
                    total_cases=0,
                    total_variants=0,
                    variants=[],
                    deviations=[],
                    conformance_rate=0.0,
                    avg_case_duration_seconds=0.0,
                ),
                deviations=[],
            )

        # Group events by case_id
        cases = defaultdict(list)
        for event in request.events:
            cases[event.case_id].append(event)

        # Sort events within each case by timestamp
        for case_id in cases:
            cases[case_id].sort(key=lambda e: e.timestamp)

        # Extract activity sequences for each case
        variant_sequences = defaultdict(list)
        case_durations = {}

        for case_id, case_events in cases.items():
            sequence = tuple(e.activity for e in case_events)
            variant_sequences[sequence].append(case_id)

            # Calculate case duration
            if len(case_events) >= 2:
                duration = (
                    case_events[-1].timestamp - case_events[0].timestamp
                ).total_seconds()
                case_durations[case_id] = duration

        # Create ProcessVariant objects
        total_cases = len(cases)
        variants = []

        for idx, (sequence, case_ids) in enumerate(
            sorted(variant_sequences.items(), key=lambda x: len(x[1]), reverse=True)
        ):
            frequency = len(case_ids)
            frequency_percentage = (frequency / total_cases) * 100

            # Calculate duration statistics for this variant
            durations = [case_durations.get(cid, 0) for cid in case_ids if cid in case_durations]

            if durations:
                avg_duration = statistics.mean(durations)
                median_duration = statistics.median(durations)
                min_duration = min(durations)
                max_duration = max(durations)
            else:
                avg_duration = median_duration = min_duration = max_duration = 0.0

            variant = ProcessVariant(
                variant_id=f"VAR_{idx:03d}",
                activity_sequence=list(sequence),
                frequency=frequency,
                frequency_percentage=frequency_percentage,
                avg_duration_seconds=avg_duration,
                median_duration_seconds=median_duration,
                min_duration_seconds=min_duration,
                max_duration_seconds=max_duration,
                is_happy_path=(idx == 0),  # Most frequent is happy path
            )
            variants.append(variant)

        # Calculate conformance rate (simplified)
        conformance_rate = (
            variants[0].frequency_percentage if variants else 0.0
        )

        # Calculate average case duration
        avg_case_duration = (
            statistics.mean(case_durations.values()) if case_durations else 0.0
        )

        # Detect deviations (simplified - would use reference model in production)
        deviations = []

        variant_summary = VariantSummary(
            total_cases=total_cases,
            total_variants=len(variants),
            variants=variants,
            deviations=deviations,
            conformance_rate=conformance_rate,
            avg_case_duration_seconds=avg_case_duration,
        )

        return CorrelateVariantsResponse(
            variant_summary=variant_summary, deviations=deviations
        )

    def predict_kpi(self, request: PredictKPIRequest) -> PredictKPIResponse:
        """
        Predict KPI using quantized local ML model.

        Args:
            request: KPI prediction request

        Returns:
            PredictKPIResponse with forecast and recommendations
        """
        logger.info(f"Predicting KPI: {request.kpi_type}")

        # TODO: Implement actual ML-based prediction
        # This would use:
        # - Quantized ONNX models for edge deployment
        # - Time series forecasting (Prophet, ARIMA)
        # - Anomaly detection models

        # Placeholder prediction based on variant summary
        avg_duration = request.variant_summary.avg_case_duration_seconds

        if request.kpi_type == "delay":
            predicted_value = avg_duration * 1.1  # Predict 10% increase
            confidence_lower = avg_duration * 0.95
            confidence_upper = avg_duration * 1.25
        elif request.kpi_type == "throughput":
            predicted_value = request.variant_summary.total_cases * 1.05
            confidence_lower = predicted_value * 0.90
            confidence_upper = predicted_value * 1.15
        else:
            predicted_value = 50.0
            confidence_lower = 40.0
            confidence_upper = 60.0

        kpi_forecast = KPIForecast(
            kpi_type=request.kpi_type,
            predicted_value=predicted_value,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            prediction_timestamp=datetime.utcnow(),
            model_version="v0.1.0-quantized",
            risk_factors=["High variant count", "Increasing case duration"],
            confidence_score=75.0,
        )

        recommendations = [
            "Consider process standardization to reduce variant count",
            "Investigate activities with highest wait times",
            "Implement automated workflow for common variants",
        ]

        return PredictKPIResponse(
            kpi_forecast=kpi_forecast, recommendations=recommendations
        )

    def analyze_bottlenecks(
        self, request: AnalyzeBottlenecksRequest
    ) -> AnalyzeBottlenecksResponse:
        """
        Identify process bottlenecks and resource constraints.

        Args:
            request: Bottleneck analysis request

        Returns:
            AnalyzeBottlenecksResponse with bottlenecks and resource utilization
        """
        logger.info(f"Analyzing bottlenecks from {len(request.events)} events")

        if not request.events:
            return AnalyzeBottlenecksResponse(bottlenecks=[], resource_utilization=[])

        # Group events by case and calculate wait times
        cases = defaultdict(list)
        for event in request.events:
            cases[event.case_id].append(event)

        # Sort events within each case
        for case_id in cases:
            cases[case_id].sort(key=lambda e: e.timestamp)

        # Calculate wait times between activities
        activity_wait_times = defaultdict(list)

        for case_events in cases.values():
            for i in range(1, len(case_events)):
                prev_event = case_events[i - 1]
                curr_event = case_events[i]
                wait_time = (curr_event.timestamp - prev_event.timestamp).total_seconds()
                activity_wait_times[curr_event.activity].append(wait_time)

        # Identify bottlenecks
        bottlenecks = []
        for activity, wait_times in activity_wait_times.items():
            if not wait_times:
                continue

            avg_wait = statistics.mean(wait_times)
            p90_wait = (
                statistics.quantiles(wait_times, n=10)[8]
                if len(wait_times) > 1
                else avg_wait
            )

            # Bottleneck if P90 is significantly higher than average
            if p90_wait > avg_wait * 1.5:
                impact_score = min(100, (p90_wait / avg_wait - 1) * 50)

                bottleneck = Bottleneck(
                    activity=activity,
                    avg_wait_time_seconds=avg_wait,
                    p90_wait_time_seconds=p90_wait,
                    frequency=len(wait_times),
                    impact_score=impact_score,
                    root_cause_hypothesis="High variability in processing time",
                )
                bottlenecks.append(bottleneck)

        # Sort by impact score
        bottlenecks.sort(key=lambda b: b.impact_score, reverse=True)

        # Calculate resource utilization
        resource_activities = defaultdict(list)
        for event in request.events:
            if event.user_id:
                resource_activities[event.user_id].append(event)

        resource_utilization = []
        for resource_id, activities in resource_activities.items():
            activity_counts = Counter(e.activity for e in activities)

            durations = [
                e.duration_seconds for e in activities if e.duration_seconds
            ]
            avg_duration = statistics.mean(durations) if durations else 0.0

            # Simple utilization calculation (would need working hours in production)
            utilization = min(100, len(activities) * 10)  # Placeholder

            resource_util = ResourceUtilization(
                resource_id=resource_id,
                total_activities=len(activities),
                avg_activity_duration_seconds=avg_duration,
                utilization_percentage=utilization,
                workload_distribution=dict(activity_counts),
            )
            resource_utilization.append(resource_util)

        return AnalyzeBottlenecksResponse(
            bottlenecks=bottlenecks, resource_utilization=resource_utilization
        )

    def generate_process_map(
        self, request: GenerateProcessMapRequest
    ) -> GenerateProcessMapResponse:
        """
        Generate visual process map from event traces.

        Args:
            request: Process map generation request

        Returns:
            GenerateProcessMapResponse with map and statistics
        """
        logger.info(f"Generating {request.output_format} process map")

        if not request.events:
            return GenerateProcessMapResponse(
                process_map="",
                statistics=ProcessMapStatistics(
                    total_activities=0,
                    total_transitions=0,
                    start_activities=[],
                    end_activities=[],
                    avg_path_length=0.0,
                    max_parallel_activities=0,
                    transition_frequencies={},
                ),
                format=request.output_format,
            )

        # Extract unique activities
        activities = set(e.activity for e in request.events)

        # Build transition graph
        cases = defaultdict(list)
        for event in request.events:
            cases[event.case_id].append(event)

        # Sort events within each case
        for case_id in cases:
            cases[case_id].sort(key=lambda e: e.timestamp)

        # Count transitions
        transitions = Counter()
        start_activities = Counter()
        end_activities = Counter()
        path_lengths = []

        for case_events in cases.values():
            if not case_events:
                continue

            start_activities[case_events[0].activity] += 1
            end_activities[case_events[-1].activity] += 1
            path_lengths.append(len(case_events))

            for i in range(len(case_events) - 1):
                from_activity = case_events[i].activity
                to_activity = case_events[i + 1].activity
                transitions[(from_activity, to_activity)] += 1

        # Generate map based on format
        if request.output_format == "mermaid":
            process_map = self._generate_mermaid_map(
                activities, transitions, start_activities
            )
        elif request.output_format == "json":
            process_map = json.dumps({
                "activities": list(activities),
                "transitions": [
                    {"from": f, "to": t, "count": c}
                    for (f, t), c in transitions.items()
                ],
                "start_activities": dict(start_activities),
                "end_activities": dict(end_activities),
            }, indent=2)
        else:
            process_map = f"# Format '{request.output_format}' not yet implemented"

        # Calculate statistics
        statistics_obj = ProcessMapStatistics(
            total_activities=len(activities),
            total_transitions=len(transitions),
            start_activities=list(start_activities.keys()),
            end_activities=list(end_activities.keys()),
            avg_path_length=statistics.mean(path_lengths) if path_lengths else 0.0,
            max_parallel_activities=1,  # Simplified
            transition_frequencies={f"{f}->{t}": c for (f, t), c in transitions.items()},
        )

        return GenerateProcessMapResponse(
            process_map=process_map,
            statistics=statistics_obj,
            format=request.output_format,
        )

    def _generate_mermaid_map(
        self,
        activities: set,
        transitions: Counter,
        start_activities: Counter,
    ) -> str:
        """Generate Mermaid flowchart from process data"""
        lines = ["graph TD"]

        # Add activities as nodes with sanitized IDs
        activity_ids = {}
        for idx, activity in enumerate(sorted(activities)):
            node_id = f"A{idx}"
            activity_ids[activity] = node_id
            # Mark start activities
            if activity in start_activities:
                lines.append(f'    {node_id}["{activity}"]:::start')
            else:
                lines.append(f'    {node_id}["{activity}"]')

        # Add transitions
        for (from_act, to_act), count in transitions.most_common(50):  # Limit edges
            from_id = activity_ids[from_act]
            to_id = activity_ids[to_act]
            lines.append(f"    {from_id} -->|{count}| {to_id}")

        # Add styling
        lines.append("    classDef start fill:#90EE90")

        return "\n".join(lines)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    engine = SAPProcessIntelligence()

    if len(sys.argv) < 2:
        print("Usage: python sap_executor.py <command>")
        print("Commands: extract, correlate, predict, analyze, generate")
        sys.exit(1)

    command = sys.argv[1]
    print(f"Executing command: {command}")
