# Website Testing Framework

An intelligent automated testing framework that analyzes websites and generates relevant test scenarios.

## Features

1. Website Analysis
- Automatic structure detection
- Feature identification
- Test scenario suggestions
- One-click test execution

2. Test Generation
- Form testing
- Navigation flows
- Dynamic content
- Authentication flows

3. Test Execution
- Natural language commands
- Cross-browser support
- Screenshot capture
- Detailed reporting

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Launch the web interface:
```bash
python run_web_interface.py
```

3. Open http://localhost:5000 and:
   - Enter your website URL
   - Click "Analyze Website"
   - Review suggested test scenarios
   - Run or customize tests

## Website Analysis

The framework can analyze websites and suggest tests based on:

1. Forms Detection
- Input fields
- Validation rules
- Submit buttons
- Error handling

2. Navigation Analysis
- Menu structure
- Links and buttons
- Page flows
- Mobile responsiveness

3. Dynamic Content
- Infinite scroll
- Load more buttons
- AJAX updates
- Content changes

4. Authentication
- Login forms
- Registration
- Password reset
- Protected areas

## Example Usage

1. Analyze Website:
```plaintext
1. Enter website URL
2. Click "Analyze Website"
3. Review detected features
4. Choose suggested tests
```

2. Run Generated Tests:
```plaintext
1. Click "Try It" on any suggestion
2. Review test steps
3. Click "Run Tests"
4. View results
```

3. Customize Tests:
```plaintext
1. Start with suggested tests
2. Modify steps as needed
3. Add additional verifications
4. Run customized tests
```

## Command Line Usage

You can also run tests from the command line:
```bash
python src/main.py -t examples/test_scenarios.yaml -u https://your-website.com
```

Options:
```
-t, --tests     Test scenarios file
-u, --url       Target website URL
-c, --config    Config file path
--browser       chrome/firefox
--headless     Run headless
```

## Project Structure

```
automation-testing/
├── src/
│   ├── web_analyzer/      # Website analysis
│   │   ├── site_analyzer.py
│   │   ├── dom_parser.py
│   │   └── element_classifier.py
│   ├── test_engine/       # Test execution
│   ├── reporting/         # Results & logs
│   ├── utils/            # Utilities
│   └── web_interface/    # Web UI
├── examples/            # Example files
└── test_output/        # Test results
```

## Test Scenarios

You can write test scenarios in YAML:

```yaml
scenarios:
  - name: Login Test
    description: Test login functionality
    steps:
      - click on the login button
      - type "user@example.com" into the email field
      - type "password123" into the password field
      - click on submit
      - verify that dashboard appears
```

## Configuration

Configure the framework in examples/config.yaml:

```yaml
browser:
  name: chrome
  headless: false

test:
  base_url: "https://your-website.com"
  screenshot_dir: test_output/screenshots
  report_dir: test_output/reports
  log_dir: test_output/logs
```

## Requirements

- Python 3.8+
- Chrome or Firefox
- Required packages in requirements.txt

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
