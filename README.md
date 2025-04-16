
# Automated Access Review & Certification System

This application demonstrates a simplified implementation of an automated access review and certification system for the System Access Management and Permissions process.

## Features

- Risk-based scheduling of access reviews
- Automated notification generation
- One-click certification interface
- Review tracking and reporting
- Background job scheduling

## Technical Components

- **Flask**: Web application framework
- **Pandas**: Data manipulation and analysis
- **APScheduler**: Background task scheduling

## Installation

1. Ensure you have Python 3.7+ installed
2. Clone this repository 
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install required packages:
   ```
   pip install flask pandas apscheduler
   ```

## Running the Application

1. Start the application:
   ```
   python app.py
   ```
2. Open a web browser and navigate to:
   ```
   http://localhost:5000/ 0r http://127.0.0.1:5000/
   ```

## Demo Workflow

1. Access the dashboard to see overview metrics
2. Click on a reviewer link to view pending certifications
3. Approve or revoke access with optional comments
4. Check the reports page for summary statistics

## Use Cases Demonstrated

- **Risk-Based Scheduling**: Access reviews are automatically scheduled based on the risk level of access (high-risk reviewed more frequently)
- **Consolidated Reviewer Experience**: Each reviewer sees all their pending certifications in one place
- **One-Click Certification**: Streamlined approve/revoke actions with minimal effort
- **Automated Notifications**: System generates and sends notifications when reviews are due
- **Compliance Reporting**: Built-in reporting for audit and compliance purposes

## Production Considerations

For a production implementation, consider adding:

- Database backend (PostgreSQL, MySQL)
- Authentication and authorization
- API integrations with identity management systems
- Email server integration
- Enhanced security features
- Expanded reporting capabilities
- Mobile-responsive design

## Contact

This demonstration was created by Amalachukwu Adaeze Atusiuba for the Intelligent Agents and Process Automation module at National College of Ireland.