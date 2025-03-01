"""
Report Generator module for creating HTML test reports.

This module provides functionality to generate detailed, interactive HTML reports
from test execution results.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import logging
from ..test_engine.scenario_parser import TestScenario
from ..test_engine.validator import TestReport, ValidationResult

class ReportGenerator:
    """Main class for generating HTML test reports."""

    # HTML template for the report
    REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .summary-item {
            text-align: center;
        }
        .success {
            color: #28a745;
        }
        .failure {
            color: #dc3545;
        }
        .step {
            margin: 10px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .step.passed {
            border-left: 5px solid #28a745;
        }
        .step.failed {
            border-left: 5px solid #dc3545;
        }
        .step-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
        }
        .details {
            display: none;
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        .step:hover .details {
            display: block;
        }
        .metrics {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            margin-top: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .expand-button {
            background: none;
            border: none;
            color: #007bff;
            cursor: pointer;
            padding: 5px 10px;
            font-size: 0.9em;
        }
        .expand-button:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Execution Report</h1>
            <h2>{{ report.scenario_name }}</h2>
            <p>Executed from {{ report.start_time }} to {{ report.end_time }}</p>
        </div>

        <div class="summary">
            <div class="summary-item">
                <h3>Total Steps</h3>
                <p>{{ report.total_steps }}</p>
            </div>
            <div class="summary-item success">
                <h3>Passed Steps</h3>
                <p>{{ report.passed_steps }}</p>
            </div>
            <div class="summary-item failure">
                <h3>Failed Steps</h3>
                <p>{{ report.failed_steps }}</p>
            </div>
            <div class="summary-item">
                <h3>Success Rate</h3>
                <p>{{ (report.passed_steps / report.total_steps * 100)|round(2) }}%</p>
            </div>
        </div>

        <div class="metrics">
            <h3>Performance Metrics</h3>
            <div class="metrics-grid">
                {% for key, value in report.performance_metrics.items() %}
                <div class="summary-item">
                    <h4>{{ key|replace('_', ' ')|title }}</h4>
                    <p>{{ value }}ms</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <h3>Test Steps</h3>
        {% for result in report.results %}
        <div class="step {{ 'passed' if result.success else 'failed' }}">
            <div class="step-header">
                <h4>{{ result.message }}</h4>
                <span class="timestamp">{{ result.timestamp }}</span>
            </div>
            
            {% if result.element_state or result.error_details or result.screenshot_path %}
            <button class="expand-button">Toggle Details</button>
            <div class="details">
                {% if result.element_state %}
                <h5>Element State:</h5>
                <pre>{{ result.element_state|tojson(indent=2) }}</pre>
                {% endif %}
                
                {% if result.error_details %}
                <h5>Error Details:</h5>
                <pre>{{ result.error_details|tojson(indent=2) }}</pre>
                {% endif %}
                
                {% if result.screenshot_path %}
                <h5>Screenshot:</h5>
                <img class="screenshot" src="{{ result.screenshot_path }}" alt="Step Screenshot">
                {% endif %}
            </div>
            {% endif %}
        </div>
        {% endfor %}

        <div class="environment">
            <h3>Environment Information</h3>
            <pre>{{ report.environment_info|tojson(indent=2) }}</pre>
        </div>
    </div>

    <script>
        document.querySelectorAll('.expand-button').forEach(button => {
            button.addEventListener('click', () => {
                const details = button.nextElementSibling;
                details.style.display = details.style.display === 'none' ? 'block' : 'none';
            });
        });
    </script>
</body>
</html>
    """

    def __init__(self, output_dir: str):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory to store generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration."""
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def generate_html_report(self, report: TestReport) -> str:
        """
        Generate an HTML report from test results.

        Args:
            report: TestReport containing test results

        Returns:
            str: Path to the generated HTML report
        """
        try:
            # Create Jinja2 environment and template
            env = Environment()
            template = env.from_string(self.REPORT_TEMPLATE)

            # Format dates for display
            report_data = self._prepare_report_data(report)

            # Render the template
            html_content = template.render(report=report_data)

            # Save the report
            report_path = self._save_html_report(html_content, report.scenario_name)
            self.logger.info(f"HTML report generated: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {str(e)}")
            raise

    def _prepare_report_data(self, report: TestReport) -> Dict:
        """
        Prepare report data for template rendering.

        Args:
            report: TestReport to prepare

        Returns:
            Dict: Prepared report data
        """
        return {
            'scenario_name': report.scenario_name,
            'start_time': report.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': report.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_steps': report.total_steps,
            'passed_steps': report.passed_steps,
            'failed_steps': report.failed_steps,
            'results': [
                {
                    'success': r.success,
                    'message': r.message,
                    'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'screenshot_path': r.screenshot_path,
                    'element_state': r.element_state,
                    'error_details': r.error_details
                }
                for r in report.results
            ],
            'environment_info': report.environment_info,
            'performance_metrics': report.performance_metrics or {}
        }

    def _save_html_report(self, html_content: str, scenario_name: str) -> str:
        """
        Save the HTML report to a file.

        Args:
            html_content: The HTML content to save
            scenario_name: Name of the test scenario

        Returns:
            str: Path to the saved report
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.output_dir / f"report_{scenario_name}_{timestamp}.html"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)

    def generate_summary_report(self, reports: List[TestReport]) -> str:
        """
        Generate a summary report combining multiple test reports.

        Args:
            reports: List of TestReport objects to summarize

        Returns:
            str: Path to the generated summary report
        """
        summary = {
            'total_scenarios': len(reports),
            'total_steps': sum(r.total_steps for r in reports),
            'passed_steps': sum(r.passed_steps for r in reports),
            'failed_steps': sum(r.failed_steps for r in reports),
            'scenarios': [
                {
                    'name': r.scenario_name,
                    'success_rate': (r.passed_steps / r.total_steps * 100) if r.total_steps > 0 else 0,
                    'execution_time': (r.end_time - r.start_time).total_seconds()
                }
                for r in reports
            ]
        }

        # Save summary report as JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_path = self.output_dir / f"summary_report_{timestamp}.json"
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        return str(summary_path)