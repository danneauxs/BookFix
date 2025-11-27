"""
AI Processing Pipeline for Bookfix.

Orchestrates the execution of AI-enhanced processors with change tracking
and provides interface to the review window system.
"""

from typing import Dict, List, Optional, TYPE_CHECKING
import datetime

if TYPE_CHECKING:
    from ..context import BookfixContext

from .change_tracker import AIChangeTracker
from .service import BookfixAIService
from ..processors.ai_choices import AIChoiceProcessor
from ..processors.ai_roman import AIRomanProcessor
from ..processors.ai_numbered import AINumberedLineProcessor
from ..logging import log_message


class AIProcessingPipeline:
    """
    Coordinates AI processing across multiple modules with change tracking.

    Manages the execution order, tracks all changes, and provides
    data for the review window system.
    """

    def __init__(self, ai_config: Dict):
        """
        Initialize the AI processing pipeline.

        Args:
            ai_config: AI configuration dictionary from .data.txt
        """
        self.ai_config = ai_config
        self.change_tracker = AIChangeTracker()

        # Initialize processors with change tracker
        self.processors = {
            "choices": AIChoiceProcessor(self.change_tracker),
            "roman": AIRomanProcessor(self.change_tracker),
            "numbers": AINumberedLineProcessor(self.change_tracker),
            "numbered": AINumberedLineProcessor(
                self.change_tracker
            ),  # Support both names
        }

        # Processing statistics
        self.processing_stats = {}
        self.start_time = None
        self.end_time = None

    def process_with_ai(
        self, ctx: "BookfixContext", selected_processors: List[str] = None
    ) -> "BookfixContext":
        """
        Run AI processing pipeline on the context.

        Args:
            ctx: BookfixContext with text to process
            selected_processors: List of processor names to run, or None for all

        Returns:
            Updated BookfixContext with AI changes applied
        """
        log_message("Starting AI processing pipeline")
        self.start_time = datetime.datetime.now()

        # Set up change tracker with original text
        original_text = ctx.text
        self.change_tracker.set_text(original_text, ctx.text)

        # Determine which processors to run
        if selected_processors is None:
            selected_processors = ["choices", "roman", "numbers"]

        # Initialize processors
        initialized_processors = []
        for processor_name in selected_processors:
            if processor_name in self.processors:
                processor = self.processors[processor_name]

                # Initialize AI for this processor
                if hasattr(processor, "initialize_ai") and processor.initialize_ai(
                    self.ai_config
                ):
                    initialized_processors.append((processor_name, processor))
                    log_message(f"Initialized AI processor: {processor_name}")
                else:
                    log_message(
                        f"Failed to initialize AI processor: {processor_name}",
                        level="WARNING",
                    )

        # Process in order with each initialized processor
        for processor_name, processor in initialized_processors:
            log_message(f"Running AI processor: {processor_name}")

            try:
                if processor_name == "choices":
                    processed_text = processor.process_choices_ai(ctx)
                    ctx.text = processed_text
                elif processor_name == "roman":
                    ctx = processor.process_roman_numerals(ctx)
                elif processor_name == "numbers" or processor_name == "numbered":
                    ctx = self._process_numbers_with_tracking(processor, ctx)

                # Update change tracker with current text
                self.change_tracker.current_text = ctx.text

                # Collect statistics
                if hasattr(processor, "get_ai_statistics"):
                    self.processing_stats[processor_name] = (
                        processor.get_ai_statistics()
                    )

                log_message(f"Completed AI processor: {processor_name}")

            except Exception as e:
                log_message(
                    f"Error in AI processor {processor_name}: {e}", level="ERROR"
                )
                # Continue with other processors
                continue

        self.end_time = datetime.datetime.now()

        # Log final statistics
        total_changes = len(self.change_tracker.changes)
        processing_time = (self.end_time - self.start_time).total_seconds()

        log_message(
            f"AI processing completed: {total_changes} changes in {processing_time:.1f}s"
        )

        return ctx

    def _process_roman_with_tracking(self, processor, ctx):
        """Process Roman numerals with change tracking."""
        # Store original text for comparison
        original_text = ctx.text

        try:
            # Process with AI
            if hasattr(processor, "process_roman_numerals_ai"):
                ctx = processor.process_roman_numerals_ai(ctx)
            else:
                ctx = processor.process_roman_numerals(ctx)

            # Extract changes by comparing text (simplified approach)
            # In a full implementation, you'd modify the processor to report changes
            if original_text != ctx.text:
                # This is a simplified change detection - in practice, the processor
                # should be modified to report specific changes like the choices processor
                log_message(
                    "Roman numeral changes detected (change tracking to be enhanced)"
                )
        except Exception as e:
            log_message(f"Roman processor error: {e}", level="ERROR")
            # Continue with original context

        return ctx

    def _process_numbers_with_tracking(self, processor, ctx):
        """Process numbers with change tracking."""
        # Store original text for comparison
        original_text = ctx.text

        try:
            # Process with AI
            if hasattr(processor, "process_numbers_ai"):
                ctx = processor.process_numbers_ai(ctx)
            else:
                # Fallback to original processing
                log_message("Numbers processor fallback to original method")

            # Extract changes by comparing text (simplified approach)
            if original_text != ctx.text:
                log_message("Number changes detected (change tracking to be enhanced)")
        except Exception as e:
            log_message(f"Numbers processor error: {e}", level="ERROR")
            # Continue with original context

        return ctx

    def get_change_tracker(self) -> AIChangeTracker:
        """Get the change tracker with all recorded changes."""
        return self.change_tracker

    def get_processing_summary(self) -> Dict:
        """Get summary of processing results."""
        stats = self.change_tracker.get_statistics()

        processing_time = 0
        if self.start_time and self.end_time:
            processing_time = (self.end_time - self.start_time).total_seconds()

        return {
            "total_changes": stats["total_changes"],
            "changes_by_module": stats["module_counts"],
            "average_confidence": stats["average_confidence"],
            "processing_time": processing_time,
            "processor_stats": self.processing_stats,
            "timestamp": self.start_time.isoformat() if self.start_time else None,
        }

    def has_changes(self) -> bool:
        """Check if any changes were made during processing."""
        return len(self.change_tracker.changes) > 0

    def should_show_review(self) -> bool:
        """Determine if the review window should be shown."""
        # Show review if there are changes and AI is enabled
        return self.ai_config.get("ai_enabled", False) and self.has_changes()

    def generate_processing_report(self) -> str:
        """Generate a detailed processing report."""
        summary = self.get_processing_summary()

        report = []
        report.append("=== AI Processing Report ===")
        report.append(f"Processed at: {summary['timestamp']}")
        report.append(f"Processing time: {summary['processing_time']:.1f} seconds")
        report.append(f"Total changes made: {summary['total_changes']}")
        report.append(f"Average confidence: {summary['average_confidence']:.2f}")
        report.append("")

        report.append("Changes by Module:")
        for module, count in summary["changes_by_module"].items():
            report.append(f"  {module}: {count} changes")

        if self.processing_stats:
            report.append("")
            report.append("Processor Statistics:")
            for processor, stats in self.processing_stats.items():
                report.append(f"  {processor}:")
                for key, value in stats.items():
                    report.append(f"    {key}: {value}")

        return "\n".join(report)

    def get_ai_service(self):
        """Get the AI service from the choices processor for keyword extraction."""
        if "choices" in self.processors:
            choices_processor = self.processors["choices"]
            if hasattr(choices_processor, "ai_service"):
                return choices_processor.ai_service
        return None


def create_ai_pipeline(ai_config: Dict) -> Optional[AIProcessingPipeline]:
    """
    Create an AI processing pipeline from configuration.

    Args:
        ai_config: AI configuration dictionary

    Returns:
        AIProcessingPipeline if AI is enabled, None otherwise
    """
    if not ai_config.get("ai_enabled", False):
        log_message("AI processing disabled in configuration")
        return None

    try:
        pipeline = AIProcessingPipeline(ai_config)
        log_message("AI processing pipeline created successfully")
        return pipeline
    except Exception as e:
        log_message(f"Failed to create AI pipeline: {e}", level="ERROR")
        return None
