# src/utils/audit_logger.py
import logging
from datetime import datetime
from pathlib import Path
import json


class AuditLogger:
    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Create simulation-specific log file
        self.log_file = self.log_dir / f"simulation_{self.simulation_id}_{self.timestamp}.log"

        # Set up logging
        self.logger = logging.getLogger(f"simulation_{simulation_id}")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log_step(self, step_name: str, details: dict):
        """Log a simulation step with details"""
        self.logger.info(f"Step: {step_name}")
        self.logger.debug(f"Details: {json.dumps(details, indent=2)}")

    def log_error(self, step_name: str, error: Exception, details: dict = None):
        """Log an error with context"""
        self.logger.error(f"Error in {step_name}: {str(error)}")
        if details:
            self.logger.debug(f"Error context: {json.dumps(details, indent=2)}")

    def generate_audit_report(self):
        """Generate a formatted audit report"""
        report_file = self.log_dir / f"audit_report_{self.simulation_id}_{self.timestamp}.txt"

        with open(self.log_file, 'r') as log, open(report_file, 'w') as report:
            report.write(f"=== Emergency Response System Simulation Audit Report ===\n")
            report.write(f"Simulation ID: {self.simulation_id}\n")
            report.write(f"Time: {self.timestamp}\n")
            report.write("=" * 50 + "\n\n")

            # Process log entries
            for line in log:
                # Format and categorize log entries
                if "ERROR" in line:
                    report.write("❌ " + line)
                elif "Step:" in line:
                    report.write("\n➡️ " + line)
                elif "Details:" in line:
                    report.write("📋 " + line)
                else:
                    report.write("   " + line)

        return report_file